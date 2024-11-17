import React, { useCallback } from 'react';
import { Upload } from 'lucide-react';
import Papa from 'papaparse';
import { CourseData } from '../types';

interface CSVUploaderProps {
  onDataUpload: (data: CourseData[]) => void;
}

export function CSVUploader({ onDataUpload }: CSVUploaderProps) {
  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    Papa.parse(file, {
      complete: (results) => {
        const parsedData: CourseData[] = results.data.slice(1).map((row: any) => ({
          courseName: row[0],
          numberOfUsers: parseInt(row[1]),
          completionRate: parseFloat(row[2]),
          averageScore: parseFloat(row[3]),
          satisfactionRate: parseFloat(row[4]),
          engagementScore: parseFloat(row[5]),
          lastUpdated: row[6]
        }));
        onDataUpload(parsedData);
      },
      header: true,
      skipEmptyLines: true
    });
  }, [onDataUpload]);

  return (
    <div className="w-full p-8 border-2 border-dashed border-gray-300 rounded-lg text-center">
      <label className="cursor-pointer flex flex-col items-center space-y-2">
        <Upload className="w-12 h-12 text-gray-400" />
        <span className="text-lg font-medium text-gray-600">Upload CSV File</span>
        <span className="text-sm text-gray-500">Drag and drop or click to select</span>
        <input
          type="file"
          accept=".csv"
          onChange={handleFileUpload}
          className="hidden"
        />
      </label>
    </div>
  );
}