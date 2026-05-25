export default function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClass = size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-12 w-12' : 'h-8 w-8';
  return (
    <div className="flex items-center justify-center p-8">
      <div className={`${sizeClass} border-2 border-gray-300 border-t-emerald-500 rounded-full animate-spin`} />
    </div>
  );
}
