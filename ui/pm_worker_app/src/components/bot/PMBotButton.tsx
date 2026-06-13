import { MessageCircle } from 'lucide-react';

interface PMBotButtonProps {
  onClick: () => void;
}

export default function PMBotButton({ onClick }: PMBotButtonProps) {
  return (
    <button
      onClick={onClick}
      className="absolute bottom-16 right-4 w-12 h-12 rounded-full bg-sanguine shadow-lg flex items-center justify-center hover:bg-sanguine-dark transition-colors z-40"
    >
      <MessageCircle size={22} className="text-white" />
    </button>
  );
}
