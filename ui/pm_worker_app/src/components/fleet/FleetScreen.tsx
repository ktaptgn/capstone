import { useState } from 'react';
import FleetGrid from './FleetGrid';
import EquipmentViewer from './EquipmentViewer';
import TireHealthList from './TireHealthList';
import ExpectedPMCard from './ExpectedPMCard';
import PreviousPMCard from './PreviousPMCard';
import type { Truck, ComponentHealth, DerivedExpectedPM, PolicyId } from '../../policies/types';
import type { PolicyContext } from '../../policies/types';
import { deriveExpectedPMFromContext, getComponentHealthForTruck } from '../../selectors/dataLoader';

interface FleetScreenProps {
  trucks: Truck[];
  componentHealth: Record<string, ComponentHealth>;
  workRecordsPreviousPM: Record<string, { date: string; type: string; result: string; duration: string }[]>;
  selectedPolicy: PolicyId;
  policyContext: PolicyContext;
}

export default function FleetScreen({ trucks, componentHealth, workRecordsPreviousPM, selectedPolicy, policyContext }: FleetScreenProps) {
  const [selectedTruckId, setSelectedTruckId] = useState('T07');
  const selectedTruck = trucks.find(t => t.id === selectedTruckId);
  const health = getComponentHealthForTruck(selectedTruckId, trucks, componentHealth);
  const tires = health.components;
  const previousPM = workRecordsPreviousPM[selectedTruckId] ?? [];
  const expectedPM: DerivedExpectedPM = deriveExpectedPMFromContext(selectedTruckId, policyContext, selectedPolicy);

  return (
    <div className="flex-1 overflow-y-auto pb-4 space-y-3 px-4">
      <FleetGrid trucks={trucks} selectedTruckId={selectedTruckId} onSelectTruck={setSelectedTruckId} />

      {selectedTruck && (
        <>
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-text-main">{selectedTruck.id}</span>
            <span className="text-[11px] text-text-sub">{selectedTruck.model}</span>
          </div>

          <EquipmentViewer tires={tires} />
          <TireHealthList tires={tires} />
          <ExpectedPMCard expectedPM={expectedPM} />
          <PreviousPMCard records={previousPM} />
        </>
      )}
    </div>
  );
}
