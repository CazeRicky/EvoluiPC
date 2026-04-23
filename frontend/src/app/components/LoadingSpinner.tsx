interface LoadingSpinnerProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
}

export function LoadingSpinner({ 
  message = 'Carregando...', 
  size = 'md',
  fullScreen = true 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  const containerClass = fullScreen 
    ? 'p-4 space-y-5 pb-24 flex items-center justify-center min-h-screen'
    : 'flex items-center justify-center';

  return (
    <div className={containerClass}>
      <div className="text-center">
        <div className={`${sizeClasses[size]} border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2`} />
        <p className="text-muted-foreground">{message}</p>
      </div>
    </div>
  );
}
