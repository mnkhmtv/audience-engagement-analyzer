import client from './client';
import { Lecture, AnalysisData } from '../types';

export const lecturesApi = {
  list: () => client.get<Lecture[]>('/lectures'),

  getById: (id: string) => client.get<Lecture>(`/lectures/${id}`),

  upload: (formData: FormData) =>
    client.post<Lecture>('/lectures/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  getAnalysis: (id: string) =>
    client.get<AnalysisData>(`/lectures/${id}/analysis`),
};
