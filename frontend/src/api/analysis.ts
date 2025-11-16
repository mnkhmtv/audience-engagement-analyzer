import client from './client';

export const analysisApi = {
  analyzeVideo: (lectureId: string, videoFile: File) => {
    const formData = new FormData();
    formData.append('file', videoFile);

    return client.post('/analysis/video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: { lecture_id: lectureId },
    });
  },
};
