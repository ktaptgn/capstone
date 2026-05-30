import { useState, useRef, useEffect, useMemo } from 'react';
import { X, Send, Bot, User } from 'lucide-react';
import { chatbotResponses, deriveExpectedPMFromContext } from '../../selectors/dataLoader';
import type { PolicyId } from '../../policies/types';
import type { PolicyContext } from '../../policies/types';

interface PMBotSheetProps {
  open: boolean;
  onClose: () => void;
  selectedPolicy: PolicyId;
  policyContext: PolicyContext;
}

interface Message {
  role: 'user' | 'bot';
  text: string;
}

function matchTruck(input: string): string | null {
  const match = input.match(/T\d{2}/i);
  return match ? match[0].toUpperCase() : null;
}

function generateBotResponse(input: string, selectedPolicy: PolicyId, policyContext: PolicyContext): string {
  const truckId = matchTruck(input);
  const lower = input.toLowerCase();

  if (!truckId) {
    return 'PM 도움말은 예상 PM 시점, 예상 소요시간, PM 선정 이유만 답변합니다.\n\n예: "T07 PM 시점", "T03 소요시간", "T01 PM 이유"';
  }

  // Verify truck exists
  const truckExists = policyContext.trucks.some(t => t.id === truckId);
  if (!truckExists) {
    return `${truckId}은(는) 등록되지 않은 트럭입니다.\n\n사용 가능한 트럭: T01~T25`;
  }

  const chatData = (chatbotResponses as Record<string, typeof chatbotResponses[keyof typeof chatbotResponses]>)[truckId];
  const derived = deriveExpectedPMFromContext(truckId, policyContext, selectedPolicy);
  const truck = policyContext.trucks.find(t => t.id === truckId);

  if (lower.includes('reason') || lower.includes('이유') || lower.includes('why')) {
    if (chatData) {
      const r = chatData.queries.policyReason.answer;
      return `${r.title}\n\n예상 PM: ${r.expectedPm}\n예상 소요시간: ${r.estimatedDuration}\n\nPM 선정 이유:\n${r.reasons.map(s => `• ${s}`).join('\n')}\n\n[Policy: ${selectedPolicy}]`;
    }
    return `${truckId} PM 판단 결과\n\nHI: ${truck?.healthIndex ?? 'N/A'}%\n상태: ${truck?.status ?? 'N/A'}\n예상 PM: ${derived.expectedPmTime}\n예상 소요시간: ${derived.estimatedDuration}\n\nPM 선정 이유: ${derived.reason}\n\n[Policy: ${selectedPolicy}]`;
  }

  if (lower.includes('duration') || lower.includes('소요') || lower.includes('시간') || lower.includes('how long')) {
    const answer = chatData?.queries.estimatedDuration.answer ?? derived.estimatedDuration;
    return `${truckId} PM 소요시간: ${answer}\n\n[Policy: ${selectedPolicy}]`;
  }

  if (lower.includes('time') || lower.includes('시점') || lower.includes('when') || lower.includes('due') || lower.includes('pm') || lower.includes('상태') || lower.includes('status')) {
    if (chatData) {
      const answer = chatData.queries.expectedPmTime.answer;
      return `${truckId} 예상 PM 시점: ${answer}\n\n[Policy: ${selectedPolicy}]`;
    }
    return `${truckId} 상태 정보\n\nHI: ${truck?.healthIndex ?? 'N/A'}%\n상태: ${truck?.status ?? 'N/A'}\nPM 예정: ${derived.expectedPmTime}\n예상 소요시간: ${derived.estimatedDuration}\n\n[Policy: ${selectedPolicy}]`;
  }

  return `${truckId} 상태 정보\n\nHI: ${truck?.healthIndex ?? 'N/A'}%\n상태: ${truck?.status ?? 'N/A'}\nPM 예정: ${derived.expectedPmTime}\n\n질문 예시: "${truckId} PM 시점", "${truckId} 소요시간", "${truckId} PM 이유"`;
}

export default function PMBotSheet({ open, onClose, selectedPolicy, policyContext }: PMBotSheetProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', text: 'PM 도움말입니다. 모든 트럭(T01~T25)에 대해 PM 시점, 소요시간, PM 선정 이유를 질문해 주세요.' },
  ]);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  // Dynamic quick actions — categorized representative suggestions
  const quickActions = useMemo(() => {
    const trucks = [...policyContext.trucks];
    const actions: { label: string; query: string }[] = [];

    // 1) 긴급PM요청 — trucks with critical/high priority → show "이유" (2 trucks)
    const criticalTrucks = trucks
      .filter(t => t.priority === 'HIGH' || t.healthIndex < 50)
      .sort((a, b) => a.healthIndex - b.healthIndex)
      .slice(0, 2);
    criticalTrucks.forEach(t => {
      actions.push({ label: `${t.id} 긴급 이유`, query: `${t.id} PM 이유` });
    });

    // 2) 우선순위 PM 대상 — next trucks by pmDue → show "PM 시점" (2 trucks)
    const priorityTrucks = trucks
      .filter(t => !criticalTrucks.find(c => c.id === t.id))
      .filter(t => t.status !== 'standby')
      .sort((a, b) => a.healthIndex - b.healthIndex)
      .slice(0, 2);
    priorityTrucks.forEach(t => {
      actions.push({ label: `${t.id} PM시점`, query: `${t.id} PM 시점` });
    });

    // 3) HI ≤ 65% — trucks with low HI → show "상태" (2 trucks)
    const lowHITrucks = trucks
      .filter(t =>
        t.healthIndex <= 65
        && !criticalTrucks.find(c => c.id === t.id)
        && !priorityTrucks.find(p => p.id === t.id)
      )
      .sort((a, b) => a.healthIndex - b.healthIndex)
      .slice(0, 2);
    lowHITrucks.forEach(t => {
      actions.push({ label: `${t.id} 상태`, query: `${t.id} 상태` });
    });

    return actions;
  }, [policyContext.trucks]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const handleSend = (text?: string) => {
    const query = text ?? input.trim();
    if (!query) return;
    setMessages(prev => [...prev, { role: 'user', text: query }]);
    setInput('');
    setTimeout(() => {
      const response = generateBotResponse(query, selectedPolicy, policyContext);
      setMessages(prev => [...prev, { role: 'bot', text: response }]);
    }, 300);
  };

  if (!open) return null;

  return (
    <div className="absolute inset-0 z-50 flex flex-col">
      <div className="flex-1 bg-black/30" onClick={onClose} />
      <div className="bg-white rounded-t-2xl flex flex-col" style={{ height: '65%' }}>
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-sanguine flex items-center justify-center">
              <Bot size={14} className="text-white" />
            </div>
            <span className="text-sm font-semibold text-text-main">PM 도움말</span>
            <span className="text-[9px] bg-sanguine-soft text-sanguine px-1.5 py-0.5 rounded-full">{selectedPolicy}</span>
          </div>
          <button onClick={onClose} className="p-1">
            <X size={18} className="text-text-sub" />
          </button>
        </div>

        {/* Quick Actions — dynamic based on truck health */}
        <div className="flex gap-1.5 px-4 py-2 overflow-x-auto no-scrollbar">
          {quickActions.map(action => (
            <button
              key={action.query}
              onClick={() => handleSend(action.query)}
              className="text-[10px] bg-sanguine-soft text-sanguine px-2.5 py-1 rounded-full whitespace-nowrap hover:bg-sanguine hover:text-white transition-colors"
            >
              {action.label}
            </button>
          ))}
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-2 space-y-3">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'bot' && (
                <div className="w-6 h-6 rounded-full bg-sanguine-soft flex items-center justify-center shrink-0">
                  <Bot size={12} className="text-sanguine" />
                </div>
              )}
              <div
                className={`max-w-[75%] px-3 py-2 rounded-xl text-[12px] leading-relaxed whitespace-pre-line ${
                  msg.role === 'user'
                    ? 'bg-sanguine text-white rounded-br-sm'
                    : 'bg-gray-100 text-text-main rounded-bl-sm'
                }`}
              >
                {msg.text}
              </div>
              {msg.role === 'user' && (
                <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center shrink-0">
                  <User size={12} className="text-text-sub" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="px-4 py-3 border-t border-border flex gap-2">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="트럭 ID + 질문 (예: T01 PM 이유)"
            className="flex-1 text-sm bg-gray-50 rounded-full px-4 py-2 outline-none border border-border focus:border-sanguine"
          />
          <button
            onClick={() => handleSend()}
            className="w-9 h-9 rounded-full bg-sanguine flex items-center justify-center hover:bg-sanguine-dark transition-colors"
          >
            <Send size={14} className="text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}
