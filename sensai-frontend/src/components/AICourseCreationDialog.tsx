"use client";

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Users, BookOpen, Loader2, Sparkles, FileText, Hash } from 'lucide-react';
import Toast from '@/components/Toast';

interface AICourseCreationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  schoolId: string;
}

type UserType = 'students' | 'teachers';
type CreationType = 'lessonplan' | 'assessment';
type LessonPlanType = 'chapter-based' | 'topic-based';

export default function AICourseCreationDialog({ isOpen, onClose, schoolId }: AICourseCreationDialogProps) {
  const [selectedUserType, setSelectedUserType] = useState<UserType | null>(null);
  const [selectedCreationType, setSelectedCreationType] = useState<CreationType | null>(null);
  const [selectedLessonPlanType, setSelectedLessonPlanType] = useState<LessonPlanType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [toast, setToast] = useState({ show: false, title: '', description: '', emoji: '' });

  // Chapter-based Lesson Plan Form State
  const [chapterLessonPlanForm, setChapterLessonPlanForm] = useState({
    Board: '',
    Grade: '',
    Subject: '',
    Chapter_Number: '',
    Number_of_Lecture: 1,
    Duration_of_Lecture: 45,
    Class_Strength: 30,
    Language: 'english',
    Quiz: true,
    Assignment: true,
    Structured_Output: true
  });

  // Topic-based Lesson Plan Form State
  const [topicLessonPlanForm, setTopicLessonPlanForm] = useState({
    Board: '',
    Grade: '',
    Subject: '',
    Topic: '',
    Number_of_Lecture: 1,
    Duration_of_Lecture: 45,
    Class_Strength: 30,
    Language: 'english',
    Quiz: true,
    Assignment: true,
    Structured_Output: true,
    file: null as File | null
  });

  // Student Assessment Form State
  const [assessmentForm, setAssessmentForm] = useState({
    Board: '',
    Grade: '',
    Subject: '',
    Chapter_Number: '',
    Number_of_Lecture: 1,
    Duration_of_Lecture: 45,
    Language: 'english',
    Quiz: true,
    Assignment: true,
    Structured_Output: true
  });

  const handleUserTypeSelect = (type: UserType) => {
    setSelectedUserType(type);
    setSelectedCreationType(null);
    setSelectedLessonPlanType(null);
    setResponse(null);
  };

  const handleCreationTypeSelect = (type: CreationType) => {
    setSelectedCreationType(type);
    setSelectedLessonPlanType(null);
    setResponse(null);
  };

  const handleLessonPlanTypeSelect = (type: LessonPlanType) => {
    setSelectedLessonPlanType(type);
    setResponse(null);
  };

  const handleChapterLessonPlanSubmit = async () => {
    setIsLoading(true);
    try {
      // Build query parameters for /Lesson_Plan endpoint
      const params = new URLSearchParams({
        Board: chapterLessonPlanForm.Board,
        Grade: chapterLessonPlanForm.Grade,
        Subject: chapterLessonPlanForm.Subject,
        Chapter_Number: chapterLessonPlanForm.Chapter_Number,
        Number_of_Lecture: chapterLessonPlanForm.Number_of_Lecture.toString(),
        Duration_of_Lecture: chapterLessonPlanForm.Duration_of_Lecture.toString(),
        Class_Strength: chapterLessonPlanForm.Class_Strength.toString(),
        Language: chapterLessonPlanForm.Language,
        Quiz: chapterLessonPlanForm.Quiz.toString(),
        Assignment: chapterLessonPlanForm.Assignment.toString(),
        Structured_Output: chapterLessonPlanForm.Structured_Output.toString()
      });

      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/lessonplan/Lesson_Plan?${params}`, {
        method: 'POST',
        headers: { 'accept': 'application/json' }
      });
      
      const result = await response.json();
      setResponse(result);

      setToast({
        show: true,
        title: 'Success',
        description: 'Chapter-based lesson plan generated successfully!',
        emoji: '✨'
      });
    } catch (error) {
      setToast({
        show: true,
        title: 'Error',
        description: 'Failed to generate chapter-based lesson plan',
        emoji: '❌'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTopicLessonPlanSubmit = async () => {
    setIsLoading(true);
    try {
      // Build query parameters for /Lesson_Plan_from_Topic endpoint
      const params = new URLSearchParams({
        Board: topicLessonPlanForm.Board,
        Grade: topicLessonPlanForm.Grade,
        Subject: topicLessonPlanForm.Subject,
        Topic: topicLessonPlanForm.Topic,
        Number_of_Lecture: topicLessonPlanForm.Number_of_Lecture.toString(),
        Duration_of_Lecture: topicLessonPlanForm.Duration_of_Lecture.toString(),
        Class_Strength: topicLessonPlanForm.Class_Strength.toString(),
        Language: topicLessonPlanForm.Language,
        Quiz: topicLessonPlanForm.Quiz.toString(),
        Assignment: topicLessonPlanForm.Assignment.toString(),
        Structured_Output: topicLessonPlanForm.Structured_Output.toString()
      });

      const formData = new FormData();
      if (topicLessonPlanForm.file) {
        formData.append('file', topicLessonPlanForm.file);
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/lessonplan/Lesson_Plan_from_Topic?${params}`, {
        method: 'POST',
        headers: { 'accept': 'application/json' },
        body: formData
      });
      
      const result = await response.json();
      setResponse(result);

      setToast({
        show: true,
        title: 'Success',
        description: 'Topic-based lesson plan generated successfully!',
        emoji: '✨'
      });
    } catch (error) {
      setToast({
        show: true,
        title: 'Error',
        description: 'Failed to generate topic-based lesson plan',
        emoji: '❌'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAssessmentSubmit = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/student/assessment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(assessmentForm)
      });
      const result = await response.json();
      setResponse(result);
      
      setToast({
        show: true,
        title: 'Success',
        description: 'Assessment session started successfully!',
        emoji: '✨'
      });
    } catch (error) {
      setToast({
        show: true,
        title: 'Error',
        description: 'Failed to start assessment',
        emoji: '❌'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setSelectedUserType(null);
    setSelectedCreationType(null);
    setSelectedLessonPlanType(null);
    setResponse(null);
    setChapterLessonPlanForm({
      Board: '',
      Grade: '',
      Subject: '',
      Chapter_Number: '',
      Number_of_Lecture: 1,
      Duration_of_Lecture: 45,
      Class_Strength: 30,
      Language: 'english',
      Quiz: true,
      Assignment: true,
      Structured_Output: true
    });
    setTopicLessonPlanForm({
      Board: '',
      Grade: '',
      Subject: '',
      Topic: '',
      Number_of_Lecture: 1,
      Duration_of_Lecture: 45,
      Class_Strength: 30,
      Language: 'english',
      Quiz: true,
      Assignment: true,
      Structured_Output: true,
      file: null
    });
    setAssessmentForm({
      Board: '',
      Grade: '',
      Subject: '',
      Chapter_Number: '',
      Number_of_Lecture: 1,
      Duration_of_Lecture: 45,
      Language: 'english',
      Quiz: true,
      Assignment: true,
      Structured_Output: true
    });
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  return (
    <>
      <Dialog open={isOpen} onOpenChange={handleClose}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-white text-black border-0 shadow-2xl">
          <DialogHeader className="pb-6">
            <DialogTitle className="flex items-center gap-3 text-2xl font-light">
              <div className="p-2 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              Create Courses with AI
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-6">
            {/* Step 1: Select User Type */}
            {!selectedUserType && (
              <div className="space-y-4">
                <h3 className="text-lg font-light">Who is this for?</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card 
                    className="cursor-pointer hover:shadow-lg transition-all duration-200 border-2 hover:border-purple-200 group"
                    onClick={() => handleUserTypeSelect('students')}
                  >
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center gap-3 text-lg font-light">
                        <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                          <Users className="w-5 h-5 text-blue-600" />
                        </div>
                        Students
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 leading-relaxed">
                        Create interactive assessments and learning materials for students
                      </p>
                    </CardContent>
                  </Card>
                  <Card 
                    className="cursor-pointer hover:shadow-lg transition-all duration-200 border-2 hover:border-purple-200 group"
                    onClick={() => handleUserTypeSelect('teachers')}
                  >
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center gap-3 text-lg font-light">
                        <div className="p-2 bg-purple-100 rounded-lg group-hover:bg-purple-200 transition-colors">
                          <BookOpen className="w-5 h-5 text-purple-600" />
                        </div>
                        Teachers
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 leading-relaxed">
                        Generate comprehensive lesson plans and teaching materials
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}

            {/* Step 2: Select Creation Type */}
            {selectedUserType && !selectedCreationType && (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setSelectedUserType(null)}
                    className="hover:bg-gray-100 rounded-full px-3"
                  >
                    ← Back
                  </Button>
                  <h3 className="text-xl font-light">
                    What would you like to create for {selectedUserType}?
                  </h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedUserType === 'teachers' && (
                    <Card 
                      className="cursor-pointer hover:bg-gray-50 transition-colors"
                      onClick={() => handleCreationTypeSelect('lessonplan')}
                    >
                      <CardHeader>
                        <CardTitle>Lesson Plans</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-gray-600">
                          Generate detailed lesson plans with activities, quizzes, and assignments
                        </p>
                      </CardContent>
                    </Card>
                  )}
                  {selectedUserType === 'students' && (
                    <Card 
                      className="cursor-pointer hover:bg-gray-50 transition-colors"
                      onClick={() => handleCreationTypeSelect('assessment')}
                    >
                      <CardHeader>
                        <CardTitle>Student Assessment</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-gray-600">
                          Create interactive assessment sessions for students
                        </p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </div>
            )}

            {/* Step 3: Select Lesson Plan Type (for teachers only) */}
            {selectedUserType === 'teachers' && selectedCreationType === 'lessonplan' && !selectedLessonPlanType && (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setSelectedCreationType(null)}
                    className="hover:bg-gray-100 rounded-full px-3"
                  >
                    ← Back
                  </Button>
                  <h3 className="text-xl font-light">
                    Choose your lesson plan type:
                  </h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card 
                    className="cursor-pointer hover:shadow-lg transition-all duration-200 border-2 hover:border-green-200 group"
                    onClick={() => handleLessonPlanTypeSelect('chapter-based')}
                  >
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center gap-3 text-lg font-light">
                        <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
                          <Hash className="w-5 h-5 text-green-600" />
                        </div>
                        Chapter-based Lesson Plan
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 leading-relaxed">
                        Generate lesson plans based on chapter number from the curriculum
                      </p>
                    </CardContent>
                  </Card>
                  <Card 
                    className="cursor-pointer hover:shadow-lg transition-all duration-200 border-2 hover:border-orange-200 group"
                    onClick={() => handleLessonPlanTypeSelect('topic-based')}
                  >
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center gap-3 text-lg font-light">
                        <div className="p-2 bg-orange-100 rounded-lg group-hover:bg-orange-200 transition-colors">
                          <FileText className="w-5 h-5 text-orange-600" />
                        </div>
                        Topic-based Lesson Plan
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 leading-relaxed">
                        Generate lesson plans based on a specific topic with optional PDF upload
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}

            {/* Step 4: Forms */}
            {selectedUserType && selectedCreationType && (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => {
                      if (selectedUserType === 'teachers' && selectedCreationType === 'lessonplan') {
                        setSelectedLessonPlanType(null);
                      } else {
                        setSelectedCreationType(null);
                      }
                    }}
                    className="hover:bg-gray-100 rounded-full px-3"
                  >
                    ← Back
                  </Button>
                  <h3 className="text-xl font-light">
                    {selectedCreationType === 'lessonplan' 
                      ? `${selectedLessonPlanType === 'chapter-based' ? 'Chapter-based' : 'Topic-based'} Lesson Plan Details`
                      : 'Assessment Details'
                    }
                  </h3>
                </div>

                {/* Chapter-based Lesson Plan Form */}
                {selectedCreationType === 'lessonplan' && selectedLessonPlanType === 'chapter-based' && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="chapter-board" className="text-sm font-medium text-gray-700">Board</Label>
                        <Input
                          id="chapter-board"
                          value={chapterLessonPlanForm.Board}
                          onChange={(e) => setChapterLessonPlanForm(prev => ({ ...prev, Board: e.target.value }))}
                          placeholder="e.g., CBSE, ICSE"
                          className="border-gray-300 focus:border-purple-500 focus:ring-purple-500"
                        />
                      </div>
                      <div>
                        <Label htmlFor="chapter-grade">Grade</Label>
                        <Input
                          id="chapter-grade"
                          value={chapterLessonPlanForm.Grade}
                          onChange={(e) => setChapterLessonPlanForm(prev => ({ ...prev, Grade: e.target.value }))}
                          placeholder="e.g., 10th"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="chapter-subject">Subject</Label>
                        <Input
                          id="chapter-subject"
                          value={chapterLessonPlanForm.Subject}
                          onChange={(e) => setChapterLessonPlanForm(prev => ({ ...prev, Subject: e.target.value }))}
                          placeholder="e.g., Mathematics"
                        />
                      </div>
                      <div>
                        <Label htmlFor="chapter-language">Language</Label>
                        <select
                          id="chapter-language"
                          value={chapterLessonPlanForm.Language}
                          onChange={(e) => setChapterLessonPlanForm(prev => ({ ...prev, Language: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="english">English</option>
                          <option value="hindi">Hindi</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <Label htmlFor="chapter-number">Chapter Number</Label>
                        <Input
                          id="chapter-number"
                          value={chapterLessonPlanForm.Chapter_Number}
                          onChange={(e) => setChapterLessonPlanForm(prev => ({ ...prev, Chapter_Number: e.target.value }))}
                          placeholder="e.g., 1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="chapter-lectures">Number of Lectures</Label>
                        <Input
                          id="chapter-lectures"
                          type="number"
                          value={chapterLessonPlanForm.Number_of_Lecture}
                          onChange={(e) => setChapterLessonPlanForm(prev => ({ ...prev, Number_of_Lecture: parseInt(e.target.value) }))}
                          min="1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="chapter-duration">Duration (minutes)</Label>
                        <Input
                          id="chapter-duration"
                          type="number"
                          value={chapterLessonPlanForm.Duration_of_Lecture}
                          onChange={(e) => setChapterLessonPlanForm(prev => ({ ...prev, Duration_of_Lecture: parseInt(e.target.value) }))}
                          min="15"
                        />
                      </div>
                      <div>
                        <Label htmlFor="chapter-strength">Class Strength</Label>
                        <Input
                          id="chapter-strength"
                          type="number"
                          value={chapterLessonPlanForm.Class_Strength}
                          onChange={(e) => setChapterLessonPlanForm(prev => ({ ...prev, Class_Strength: parseInt(e.target.value) }))}
                          min="1"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="chapter-quiz"
                          checked={chapterLessonPlanForm.Quiz}
                          onChange={(e) => setChapterLessonPlanForm(prev => ({ ...prev, Quiz: e.target.checked }))}
                        />
                        <Label htmlFor="chapter-quiz">Include Quiz</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="chapter-assignment"
                          checked={chapterLessonPlanForm.Assignment}
                          onChange={(e) => setChapterLessonPlanForm(prev => ({ ...prev, Assignment: e.target.checked }))}
                        />
                        <Label htmlFor="chapter-assignment">Include Assignment</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="chapter-structured"
                          checked={chapterLessonPlanForm.Structured_Output}
                          onChange={(e) => setChapterLessonPlanForm(prev => ({ ...prev, Structured_Output: e.target.checked }))}
                        />
                        <Label htmlFor="chapter-structured">Structured Output</Label>
                      </div>
                    </div>

                    <Button 
                      onClick={handleChapterLessonPlanSubmit} 
                      disabled={isLoading}
                      className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-medium py-3 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Generating Chapter-based Lesson Plan...
                        </>
                      ) : (
                        'Generate Chapter-based Lesson Plan'
                      )}
                    </Button>
                  </div>
                )}

                {/* Topic-based Lesson Plan Form */}
                {selectedCreationType === 'lessonplan' && selectedLessonPlanType === 'topic-based' && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="topic-board">Board</Label>
                        <Input
                          id="topic-board"
                          value={topicLessonPlanForm.Board}
                          onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, Board: e.target.value }))}
                          placeholder="e.g., CBSE, ICSE"
                        />
                      </div>
                      <div>
                        <Label htmlFor="topic-grade">Grade</Label>
                        <Input
                          id="topic-grade"
                          value={topicLessonPlanForm.Grade}
                          onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, Grade: e.target.value }))}
                          placeholder="e.g., 10th"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="topic-subject">Subject</Label>
                        <Input
                          id="topic-subject"
                          value={topicLessonPlanForm.Subject}
                          onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, Subject: e.target.value }))}
                          placeholder="e.g., Mathematics"
                        />
                      </div>
                      <div>
                        <Label htmlFor="topic-language">Language</Label>
                        <select
                          id="topic-language"
                          value={topicLessonPlanForm.Language}
                          onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, Language: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="english">English</option>
                          <option value="hindi">Hindi</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="topic-name">Topic</Label>
                      <Input
                        id="topic-name"
                        value={topicLessonPlanForm.Topic}
                        onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, Topic: e.target.value }))}
                        placeholder="e.g., Quadratic Equations"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <Label htmlFor="topic-lectures">Number of Lectures</Label>
                        <Input
                          id="topic-lectures"
                          type="number"
                          value={topicLessonPlanForm.Number_of_Lecture}
                          onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, Number_of_Lecture: parseInt(e.target.value) }))}
                          min="1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="topic-duration">Duration (minutes)</Label>
                        <Input
                          id="topic-duration"
                          type="number"
                          value={topicLessonPlanForm.Duration_of_Lecture}
                          onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, Duration_of_Lecture: parseInt(e.target.value) }))}
                          min="15"
                        />
                      </div>
                      <div>
                        <Label htmlFor="topic-strength">Class Strength</Label>
                        <Input
                          id="topic-strength"
                          type="number"
                          value={topicLessonPlanForm.Class_Strength}
                          onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, Class_Strength: parseInt(e.target.value) }))}
                          min="1"
                        />
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="topic-file">Upload PDF (Optional)</Label>
                      <Input
                        id="topic-file"
                        type="file"
                        accept=".pdf"
                        onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, file: e.target.files?.[0] || null }))}
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="topic-quiz"
                          checked={topicLessonPlanForm.Quiz}
                          onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, Quiz: e.target.checked }))}
                        />
                        <Label htmlFor="topic-quiz">Include Quiz</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="topic-assignment"
                          checked={topicLessonPlanForm.Assignment}
                          onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, Assignment: e.target.checked }))}
                        />
                        <Label htmlFor="topic-assignment">Include Assignment</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="topic-structured"
                          checked={topicLessonPlanForm.Structured_Output}
                          onChange={(e) => setTopicLessonPlanForm(prev => ({ ...prev, Structured_Output: e.target.checked }))}
                        />
                        <Label htmlFor="topic-structured">Structured Output</Label>
                      </div>
                    </div>

                    <Button 
                      onClick={handleTopicLessonPlanSubmit} 
                      disabled={isLoading}
                      className="w-full bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 text-white font-medium py-3 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Generating Topic-based Lesson Plan...
                        </>
                      ) : (
                        'Generate Topic-based Lesson Plan'
                      )}
                    </Button>
                  </div>
                )}

                {/* Student Assessment Form */}
                {selectedCreationType === 'assessment' && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="assessment-board">Board</Label>
                        <Input
                          id="assessment-board"
                          value={assessmentForm.Board}
                          onChange={(e) => setAssessmentForm(prev => ({ ...prev, Board: e.target.value }))}
                          placeholder="e.g., CBSE, ICSE"
                        />
                      </div>
                      <div>
                        <Label htmlFor="assessment-grade">Grade</Label>
                        <Input
                          id="assessment-grade"
                          value={assessmentForm.Grade}
                          onChange={(e) => setAssessmentForm(prev => ({ ...prev, Grade: e.target.value }))}
                          placeholder="e.g., 10th"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="assessment-subject">Subject</Label>
                        <Input
                          id="assessment-subject"
                          value={assessmentForm.Subject}
                          onChange={(e) => setAssessmentForm(prev => ({ ...prev, Subject: e.target.value }))}
                          placeholder="e.g., Mathematics"
                        />
                      </div>
                      <div>
                        <Label htmlFor="assessment-language">Language</Label>
                        <select
                          id="assessment-language"
                          value={assessmentForm.Language}
                          onChange={(e) => setAssessmentForm(prev => ({ ...prev, Language: e.target.value }))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="english">English</option>
                          <option value="hindi">Hindi</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <Label htmlFor="assessment-chapter">Chapter Number</Label>
                        <Input
                          id="assessment-chapter"
                          value={assessmentForm.Chapter_Number}
                          onChange={(e) => setAssessmentForm(prev => ({ ...prev, Chapter_Number: e.target.value }))}
                          placeholder="e.g., 1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="assessment-lectures">Number of Lectures</Label>
                        <Input
                          id="assessment-lectures"
                          type="number"
                          value={assessmentForm.Number_of_Lecture}
                          onChange={(e) => setAssessmentForm(prev => ({ ...prev, Number_of_Lecture: parseInt(e.target.value) }))}
                          min="1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="assessment-duration">Duration (minutes)</Label>
                        <Input
                          id="assessment-duration"
                          type="number"
                          value={assessmentForm.Duration_of_Lecture}
                          onChange={(e) => setAssessmentForm(prev => ({ ...prev, Duration_of_Lecture: parseInt(e.target.value) }))}
                          min="15"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="assessment-quiz"
                          checked={assessmentForm.Quiz}
                          onChange={(e) => setAssessmentForm(prev => ({ ...prev, Quiz: e.target.checked }))}
                        />
                        <Label htmlFor="assessment-quiz">Include Quiz</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="assessment-assignment"
                          checked={assessmentForm.Assignment}
                          onChange={(e) => setAssessmentForm(prev => ({ ...prev, Assignment: e.target.checked }))}
                        />
                        <Label htmlFor="assessment-assignment">Include Assignment</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="assessment-structured"
                          checked={assessmentForm.Structured_Output}
                          onChange={(e) => setAssessmentForm(prev => ({ ...prev, Structured_Output: e.target.checked }))}
                        />
                        <Label htmlFor="assessment-structured">Structured Output</Label>
                      </div>
                    </div>

                    <Button 
                      onClick={handleAssessmentSubmit} 
                      disabled={isLoading}
                      className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-medium py-3 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Starting Assessment...
                        </>
                      ) : (
                        'Start Assessment Session'
                      )}
                    </Button>
                  </div>
                )}
              </div>
            )}

            {/* Response Display */}
            {response && (
              <div className="space-y-4">
                <h3 className="text-lg font-light">Generated Response</h3>
                <Card>
                  <CardContent className="pt-6">
                    <div className="space-y-6 max-h-96 overflow-y-auto">
                      {response.status && (
                        <div className="flex items-center gap-2">
                          <div className={`w-3 h-3 rounded-full ${response.status === 'success' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                          <span className="text-sm font-medium capitalize">{response.status}</span>
                        </div>
                      )}
                      
                      {response.message && (
                        <div className="p-3 bg-blue-50 rounded-lg">
                          <p className="text-sm text-blue-800">{response.message}</p>
                        </div>
                      )}
                      
                      {response.data && Array.isArray(response.data) && response.data.map((item: any, index: number) => (
                        <div key={index} className="space-y-4">
                          {Object.entries(item).map(([key, value]) => (
                            <div key={key} className="space-y-2">
                              <h4 className="text-sm font-semibold text-gray-800 capitalize">
                                {key.replace(/_/g, ' ')}
                              </h4>
                              <div className="p-3 bg-gray-50 rounded-lg">
                                {typeof value === 'string' ? (
                                  <div className="text-sm text-gray-700 whitespace-pre-wrap">
                                    {value}
                                  </div>
                                ) : (
                                  <pre className="text-sm text-gray-700 overflow-auto">
                                    {JSON.stringify(value, null, 2)}
                                  </pre>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      ))}
                      
                      {response.data && !Array.isArray(response.data) && (
                        <div className="space-y-4">
                          {Object.entries(response.data).map(([key, value]) => (
                            <div key={key} className="space-y-2">
                              <h4 className="text-sm font-semibold text-gray-800 capitalize">
                                {key.replace(/_/g, ' ')}
                              </h4>
                              <div className="p-3 bg-gray-50 rounded-lg">
                                {typeof value === 'string' ? (
                                  <div className="text-sm text-gray-700 whitespace-pre-wrap">
                                    {value}
                                  </div>
                                ) : (
                                  <pre className="text-sm text-gray-700 overflow-auto">
                                    {JSON.stringify(value, null, 2)}
                                  </pre>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
                <div className="flex gap-3">
                  <Button 
                    onClick={resetForm} 
                    variant="outline"
                    className="flex-1 border-gray-300 hover:bg-gray-50 hover:border-gray-400 font-medium py-2"
                  >
                    Create Another
                  </Button>
                  <Button 
                    onClick={handleClose}
                    className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-medium py-2 shadow-lg hover:shadow-xl"
                  >
                    Close
                  </Button>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {toast.show && (
        <Toast
          title={toast.title}
          description={toast.description}
          emoji={toast.emoji}
          onClose={() => setToast({ show: false, title: '', description: '', emoji: '' })}
        />
      )}
    </>
  );
}
