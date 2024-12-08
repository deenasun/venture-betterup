import React, { useState, useEffect } from 'react';
import { BarChart3, Settings, LogOut } from 'lucide-react';
import { Dashboard } from './components/Dashboard';
import { CourseDetails } from './components/CourseDetails';
import { LoginForm } from './components/auth/LoginForm';
import { RegisterForm } from './components/auth/RegisterForm';
import { ChangePasswordForm } from './components/auth/ChangePasswordForm';
import { useAuth } from './hooks/useAuth';
import { CourseData, AWSCourseData } from './types';
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import Papa from 'papaparse';

const s3Client = new S3Client({
  region: "us-east-1", // Replace with your bucket's region
  credentials: {
    accessKeyId: import.meta.env.VITE_AWS_ACCESS_KEY_ID ?? '',
    secretAccessKey: import.meta.env.VITE_AWS_SECRET_ACCESS_KEY ?? ''
  }
});

async function getCourseData() {
  const command = new GetObjectCommand({
    Bucket: import.meta.env.VITE_AWS_BUCKET_NAME,
    Key: import.meta.env.VITE_AWS_DATA_KEY,
  });
  const response = await s3Client.send(command);
  
  if (response?.Body) {
    const csvString = await response.Body.transformToString();

    const csvData = await new Promise((resolve, reject) => {
      Papa.parse(csvString, {
        header: true,
        complete: (results) => resolve(results.data),
        error: (err) => reject(err)
      });
    });

    const transformedData: AWSCourseData[] = csvData?.map?.((row) => {
      return {
        Code: row['Code'],
        Creationdate: row['Creation Date'],
        Age: parseFloat(row['Days Since Creation']),
        PostCourseSurvey: row['Post Course Survey'],
        Timeline: row['Timeline'],
        Title: row['Title'],
        Type: row['Type'],
        lastUpdated: '',
        Enrollment: 0, // AWS data doesn't contain
        NotStarted: 0,
        Stuck: 0,
        Completed: 0,
        Status: ''
      };
    });
    return transformedData;
  }
  else {
    return []
  }
}

// const sampleData: CourseData[] = [
//   {
//     Title: "Introduction to Python",
//     Age: 3,
//     Enrollment: 450,
//     NotStarted: 35,
//     Stuck: 25,
//     Completed: 40,
//     Status: "Active",
//     Timeline: [
//       { date: "2024-01-01", sessions: 120, completion: 45, enrollments: 80 },
//       { date: "2024-01-02", sessions: 125, completion: 48, enrollments: 85 },
//       { date: "2024-01-03", sessions: 130, completion: 50, enrollments: 90 }
//     ],
//     badges: ["Popular Choice", "Skill Builder", "Career Catalyst"],
//     recommendation: "Consider adding more interactive coding exercises to reduce the 'stuck' percentage",
//     lastUpdated: new Date().toISOString()
//   },
//   {
//     Title: "Web Development Basics",
//     Age: 2,
//     Enrollment: 380,
//     NotStarted: 40,
//     Stuck: 20,
//     Completed: 40,
//     Status: "Active",
//     Timeline: [
//       { date: "2024-01-01", sessions: 100, completion: 40, enrollments: 70 },
//       { date: "2024-01-02", sessions: 105, completion: 42, enrollments: 75 },
//       { date: "2024-01-03", sessions: 110, completion: 45, enrollments: 80 }
//     ],
//     badges: ["Up-to-Date", "Interactive Experience"],
//     recommendation: "Add more real-world project examples to improve completion rate",
//     lastUpdated: new Date().toISOString()
//   },
//   {
//     Title: "Data Science Fundamentals",
//     Age: 1,
//     Enrollment: 520,
//     NotStarted: 30,
//     Stuck: 30,
//     Completed: 40,
//     Status: "Active",
//     Timeline: [
//       { date: "2024-01-01", sessions: 140, completion: 55, enrollments: 90 },
//       { date: "2024-01-02", sessions: 145, completion: 58, enrollments: 95 },
//       { date: "2024-01-03", sessions: 150, completion: 60, enrollments: 100 }
//     ],
//     badges: ["Completion Champion", "Learners' Favorite", "Lasting Impact"],
//     recommendation: "Great performance overall, consider expanding advanced topics",
//     lastUpdated: new Date().toISOString()
//   },
//   {
//     Title: "Machine Learning Basics",
//     Age: 2,
//     Enrollment: 420,
//     NotStarted: 45,
//     Stuck: 15,
//     Completed: 40,
//     Status: "Active",
//     Timeline: [
//       { date: "2024-01-01", sessions: 110, completion: 42, enrollments: 75 },
//       { date: "2024-01-02", sessions: 115, completion: 45, enrollments: 80 },
//       { date: "2024-01-03", sessions: 120, completion: 48, enrollments: 85 }
//     ],
//     badges: ["Interactive Experience", "Skill Builder"],
//     recommendation: "Focus on reducing the not-started percentage through better onboarding",
//     lastUpdated: new Date().toISOString()
//   }
// ];

export default function App() {
  const [courseData, setCourseData] = useState<AWSCourseData[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<CourseData | null>(null);
  const [showRegister, setShowRegister] = useState(false);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>(new Date().toISOString());
  const { isAuthenticated, currentUser, login, register, logout, changePassword } = useAuth();

  useEffect(() => {
    setLastUpdated(new Date().toISOString());
    getCourseData().then((data) => {
      setCourseData(data);
    }).catch((err) => {
      console.error('Error fetching course data:', err);
    })
  }, []);

  const handleRefreshData = () => {
    // In a real application, this would trigger the scraper
    // For now, we'll just refresh the timestamps
    const updatedData = courseData.map(course => ({
      ...course,
      lastUpdated: new Date().toISOString()
    }));
    setCourseData(updatedData);
    setLastUpdated(new Date().toISOString());
  };

  const handleRegister = (username: string, password: string) => {
    const success = register(username, password);
    if (success) {
      setShowRegister(false);
      login(username, password);
    }
    return success;
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        {showRegister ? (
          <RegisterForm
            onRegister={handleRegister}
            onSwitchToLogin={() => setShowRegister(false)}
          />
        ) : (
          <LoginForm
            onLogin={login}
            onSwitchToRegister={() => setShowRegister(true)}
          />
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-primary text-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <BarChart3 className="h-8 w-8" />
              <span className="ml-2 text-xl font-semibold">Course Audit Dashboard</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm">Welcome, {currentUser}</span>
              <button
                onClick={() => setShowChangePassword(true)}
                className="p-2 rounded-full hover:bg-primary/90"
                title="Change Password"
              >
                <Settings className="w-5 h-5" />
              </button>
              <button
                onClick={logout}
                className="p-2 rounded-full hover:bg-primary/90"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {selectedCourse ? (
          <CourseDetails 
            course={selectedCourse} 
            onBack={() => setSelectedCourse(null)}
          />
        ) : (
          <Dashboard 
            data={courseData}
            onCourseSelect={setSelectedCourse}
            onRefreshData={handleRefreshData}
            lastUpdated={lastUpdated}
          />
        )}
      </main>

      {showChangePassword && currentUser && (
        <ChangePasswordForm
          username={currentUser}
          onChangePassword={changePassword}
          onClose={() => setShowChangePassword(false)}
        />
      )}
    </div>
  );
}