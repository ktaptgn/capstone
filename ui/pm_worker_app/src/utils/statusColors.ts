export function getStatusColor(status: string): string {
  switch (status) {
    case 'critical': return '#DC2626';
    case 'warning': return '#F59E0B';
    case 'watch': return '#F97316';
    case 'normal': return '#16A34A';
    case 'in-progress': return '#7C3AED';
    default: return '#6B7280';
  }
}

export function getStatusBg(status: string): string {
  switch (status) {
    case 'critical': return '#FEE2E2';
    case 'warning': return '#FEF3C7';
    case 'watch': return '#FFEDD5';
    case 'normal': return '#DCFCE7';
    case 'in-progress': return '#EDE9FE';
    default: return '#F3F4F6';
  }
}

export function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'critical': return '#DC2626';
    case 'high': return '#DC2626';
    case 'medium': return '#F59E0B';
    case 'low': return '#16A34A';
    case 'in-progress': return '#7C3AED';
    default: return '#6B7280';
  }
}

export function getPriorityBg(priority: string): string {
  switch (priority) {
    case 'critical': return '#FEE2E2';
    case 'high': return '#FEE2E2';
    case 'medium': return '#FEF3C7';
    case 'low': return '#DCFCE7';
    case 'in-progress': return '#EDE9FE';
    default: return '#F3F4F6';
  }
}

export function getHIColor(hi: number): string {
  if (hi < 40) return '#DC2626';
  if (hi < 60) return '#F59E0B';
  if (hi < 75) return '#F97316';
  return '#16A34A';
}
