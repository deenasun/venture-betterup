import React, { useState } from 'react';
import { Users, GraduationCap, Trophy, Heart, RefreshCw } from 'lucide-react';
import { CourseData, DashboardStats } from '../types';
import { StatsCard } from './StatsCard';
import { CourseTable } from './CourseTable';
import { RefreshDataModal } from './RefreshDataModal';

interface DashboardProps {
  data: CourseData[];
  onCourseSelect: (course: CourseData) => void;
  onRefreshData: () => void;
  lastUpdated: string;
}

export function Dashboard({ data, onCourseSelect, onRefreshData, lastUpdated }: DashboardProps) {
  const [showRefreshModal, setShowRefreshModal] = useState(false);

  const stats: DashboardStats = {
    totalUsers: data.reduce((sum, course) => sum + course.Enrollment, 0),
    averageCompletion: data.reduce((sum, course) => sum + course.Completed, 0) / data.length,
    totalCourses: data.length,
    averageSatisfaction: 85
  };

  const handleRefreshConfirm = () => {
    onRefreshData();
    setShowRefreshModal(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">
          Last updated: {new Date(lastUpdated).toLocaleString()}
        </p>
        <button
          onClick={() => setShowRefreshModal(true)}
          className="flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Data
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Users"
          value={stats.totalUsers.toLocaleString()}
          icon={Users}
          trend={5.2}
        />
        <StatsCard
          title="Average Completion"
          value={`${stats.averageCompletion.toFixed(1)}%`}
          icon={GraduationCap}
          trend={2.1}
        />
        <StatsCard
          title="Total Courses"
          value={stats.totalCourses}
          icon={Trophy}
        />
        <StatsCard
          title="Avg. Satisfaction"
          value={`${stats.averageSatisfaction}%`}
          icon={Heart}
          trend={1.8}
        />
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4">Course Details</h3>
        <CourseTable 
          data={data}
          onCourseClick={onCourseSelect}
        />
      </div>

      {showRefreshModal && (
        <RefreshDataModal
          onConfirm={handleRefreshConfirm}
          onCancel={() => setShowRefreshModal(false)}
        />
      )}
    </div>
  );
}