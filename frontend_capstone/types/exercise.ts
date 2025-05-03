export interface Exercise {
  _id: string;
  name: string;
  description: string;
  assigned_by: string;
  assigned_to: string;
  assigned_date: string;
  due_date: string;
  status: 'Pending' | 'Completed' | 'In Progress' | 'Not Completed';
  created_at: string;
  updated_at: string;
  video: any
  video_id : string
}

export interface ExerciseResponse {
  data: Exercise[];
  message: string;
  status: number;
} 