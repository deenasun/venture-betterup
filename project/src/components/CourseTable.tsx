import React, { useState, useMemo } from 'react';
import { ChevronRight, ChevronDown, ChevronUp } from 'lucide-react';
import { CourseData } from '../types';
import { CourseBadges } from './CourseBadges';

interface CourseTableProps {
  data: CourseData[];
  onCourseClick: (course: CourseData) => void;
}

type SortField = 'Course' | 'Enrollment' | 'NotStarted' | 'Stuck' | 'Completed';
type SortDirection = 'asc' | 'desc';

export function CourseTable({ data, onCourseClick }: CourseTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('Course');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredAndSortedData = useMemo(() => {
    return data
      .filter(course => 
        course.Course.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.badges.some(badge => badge.toLowerCase().includes(searchTerm.toLowerCase()))
      )
      .sort((a, b) => {
        const multiplier = sortDirection === 'asc' ? 1 : -1;
        const fieldA = a[sortField];
        const fieldB = b[sortField];
        
        if (typeof fieldA === 'string') {
          return multiplier * fieldA.localeCompare(fieldB as string);
        }
        return multiplier * ((fieldA as number) - (fieldB as number));
      });
  }, [data, searchTerm, sortField, sortDirection]);

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? 
      <ChevronUp className="w-4 h-4 inline-block ml-1" /> : 
      <ChevronDown className="w-4 h-4 inline-block ml-1" />;
  };

  const renderSortableHeader = (field: SortField, label: string) => (
    <th 
      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-50"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center">
        {label}
        <SortIcon field={field} />
      </div>
    </th>
  );

  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
      <div className="p-4">
        <input
          type="text"
          placeholder="Search by course name or badge..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
        />
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {renderSortableHeader('Course', 'Course')}
              {renderSortableHeader('Enrollment', 'Enrollment')}
              {renderSortableHeader('NotStarted', 'Not Started')}
              {renderSortableHeader('Stuck', 'Stuck')}
              {renderSortableHeader('Completed', 'Completed')}
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                Details
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredAndSortedData.map((course, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-900">
                      {course.Course}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {course.badges.map((badge, i) => (
                        <span
                          key={i}
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/10 text-primary"
                        >
                          {badge}
                        </span>
                      ))}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {course.Enrollment.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-primary rounded-full h-2" 
                        style={{ width: `${course.NotStarted}%` }}
                      />
                    </div>
                    {course.NotStarted}%
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-secondary rounded-full h-2" 
                        style={{ width: `${course.Stuck}%` }}
                      />
                    </div>
                    {course.Stuck}%
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-accent rounded-full h-2" 
                        style={{ width: `${course.Completed}%` }}
                      />
                    </div>
                    {course.Completed}%
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    course.Status === 'Active' 
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {course.Status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">
                  <button
                    onClick={() => onCourseClick(course)}
                    className="text-primary hover:text-primary/80 flex items-center"
                  >
                    View Details
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}