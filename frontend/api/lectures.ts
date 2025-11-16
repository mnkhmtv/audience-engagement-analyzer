import type { Lecture, Analysis, UploadPayload } from '@/types/index';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getLectures(token: string): Promise<Lecture[]> {
  const response = await fetch(`${API_URL}/lectures`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error('Failed to fetch lectures');
  return response.json();
}

export async function getLecture(token: string, id: string): Promise<Lecture> {
  const response = await fetch(`${API_URL}/lectures/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error('Failed to fetch lecture');
  return response.json();
}

export async function getAnalysis(token: string, id: string): Promise<Analysis> {
  const response = await fetch(`${API_URL}/lectures/${id}/analysis`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error('Failed to fetch analysis');
  const data = await response.json();
  return data;
}

export async function uploadLecture(
  token: string,
  payload: UploadPayload,
  onProgress?: (progress: number) => void,
): Promise<string> {
  const formData = new FormData();
  formData.append('title', payload.title);
  formData.append('subject', payload.subject);
  formData.append('video', payload.video);

  const xhr = new XMLHttpRequest();

  return new Promise((resolve, reject) => {
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable && onProgress) {
        const progress = (e.loaded / e.total) * 100;
        onProgress(progress);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        const data = JSON.parse(xhr.responseText);
        resolve(data.id);
      } else {
        reject(new Error('Upload failed'));
      }
    });

    xhr.addEventListener('error', () => reject(new Error('Upload error')));

    xhr.open('POST', `${API_URL}/lectures/upload`);
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.send(formData);
  });
}
