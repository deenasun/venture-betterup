export interface TimelineData {
  date: string;
  sessions: number;
  completion: number;
  enrollments: number;
}

export interface CourseData {
  Title: string;
  Age: number;
  Enrollment: number;
  NotStarted: number;
  Stuck: number;
  Completed: number;
  Status: string;
  Timeline: TimelineData[];
  badges: string[];
  recommendation?: string;
  lastUpdated: string;
}

export interface AWSCourseData {
  Code: string;
  CreationDate: string;
  Age: number;
  PostCourseSurvey: string;
  Timeline: TimelineData[];
  Title: string;
  Type: string;
  badges?: string[];
  recommendation?: string;
  lastUpdated: string;
  Enrollment: number;
  NotStarted: number;
  Stuck: number;
  Completed: number;
  Status: string;
}

export interface DashboardStats {
  totalUsers: number;
  averageCompletion: number;
  totalCourses: number;
  averageSatisfaction: number;
}

export interface User {
  username: string;
  password: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  currentUser: string | null;
}

export interface Badge {
  name: string;
  description: string;
  icon: string;
}