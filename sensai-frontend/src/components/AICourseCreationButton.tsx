"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';
import AICourseCreationDialog from './AICourseCreationDialog';

interface AICourseCreationButtonProps {
  schoolId: string;
  className?: string;
}

export default function AICourseCreationButton({ schoolId, className }: AICourseCreationButtonProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  return (
    <>
      <Button
        onClick={() => setIsDialogOpen(true)}
        className={`bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white ${className}`}
      >
        <Sparkles className="w-4 h-4 mr-2" />
        Create Courses with AI
      </Button>

      <AICourseCreationDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        schoolId={schoolId}
      />
    </>
  );
}
