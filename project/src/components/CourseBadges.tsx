import React from 'react';
import { Flame, CheckSquare, ThumbsUp, Users2, Brain, TrendingUp, Briefcase, LineChart } from 'lucide-react';

interface CourseBadgesProps {
  badges: string[];
}

const BADGE_CONFIG = {
  'Popular Choice': {
    icon: Flame,
    description: 'Highest number of enrolled users',
    color: 'text-primary'
  },
  'Completion Champion': {
    icon: CheckSquare,
    description: 'High completion rate of subscribers',
    color: 'text-primary'
  },
  'Up-to-Date': {
    icon: TrendingUp,
    description: 'Recently updated courses',
    color: 'text-primary'
  },
  'Learners\' Favorite': {
    icon: ThumbsUp,
    description: 'High satisfaction rate in post-course survey',
    color: 'text-secondary'
  },
  'Interactive Experience': {
    icon: Users2,
    description: 'High engagement in learning process',
    color: 'text-secondary'
  },
  'Skill Builder': {
    icon: Brain,
    description: 'Measurable improvement in learner skill',
    color: 'text-secondary'
  },
  'Career Catalyst': {
    icon: Briefcase,
    description: 'Aligns with career advancement',
    color: 'text-accent'
  },
  'Lasting Impact': {
    icon: LineChart,
    description: 'Long-term performance change',
    color: 'text-accent'
  }
};

export function CourseBadges({ badges }: CourseBadgesProps) {
  return (
    <div className="flex flex-wrap gap-4">
      {badges.map(badgeName => {
        const badge = BADGE_CONFIG[badgeName];
        if (!badge) return null;
        
        const Icon = badge.icon;
        
        return (
          <div
            key={badgeName}
            className="flex items-center space-x-2 bg-white p-3 rounded-lg shadow-sm"
          >
            <Icon className={`w-5 h-5 ${badge.color}`} />
            <div>
              <p className="font-semibold text-sm">{badgeName}</p>
              <p className="text-xs text-gray-500">{badge.description}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}