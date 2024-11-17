import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface RefreshDataModalProps {
  onConfirm: () => void;
  onCancel: () => void;
}

export function RefreshDataModal({ onConfirm, onCancel }: RefreshDataModalProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <div className="flex items-center mb-4">
          <AlertTriangle className="w-6 h-6 text-yellow-500 mr-2" />
          <h3 className="text-lg font-semibold">Confirm Data Refresh</h3>
        </div>
        
        <p className="text-gray-600 mb-6">
          Only refresh data when old data is outdated. This process may take a few moments.
        </p>

        <div className="flex justify-end space-x-4">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90"
          >
            Confirm Refresh
          </button>
        </div>
      </div>
    </div>
  );
}