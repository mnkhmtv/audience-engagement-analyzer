from __future__ import annotations

import numpy as np
import cv2
import mediapipe as mp
from typing import List, Dict, Tuple


class AttentionEstimator:
    def __init__(
        self,
        yaw_ok: float = 30.0,
        pitch_ok: float = 20.0,
        max_faces: int = 10,
        min_detection_confidence: float = 0.5,
        pad_ratio: float = 0.15,
    ):
        self.yaw_ok = yaw_ok
        self.pitch_ok = pitch_ok
        self.pad_ratio = pad_ratio
        self._mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=max_faces,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5,
        )
        self._detector = mp.solutions.face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=min_detection_confidence
        )

    def _get_head_pose(
        self, landmarks, image_w: int, image_h: int
    ) -> Tuple[float, float, float]:
        """
        Estimate head pose (yaw, pitch, roll) from MediaPipe landmarks using solvePnP.
        """
        # MediaPipe landmark indices for 3D model points
        # Using key facial landmarks
        landmark_indices = [1, 33, 61, 199, 291, 61]  # nose tip, chin, left/right eye, mouth corners
        if len(landmarks) < 468:
            return 0.0, 0.0, 0.0

        # Extract 2D points
        pts_2d = np.array(
            [
                [landmarks[1].x * image_w, landmarks[1].y * image_h],  # nose tip
                [landmarks[175].x * image_w, landmarks[175].y * image_h],  # chin
                [landmarks[33].x * image_w, landmarks[33].y * image_h],  # left eye corner
                [landmarks[263].x * image_w, landmarks[263].y * image_h],  # right eye corner
                [landmarks[61].x * image_w, landmarks[61].y * image_h],  # left mouth corner
                [landmarks[291].x * image_w, landmarks[291].y * image_h],  # right mouth corner
            ],
            dtype=np.float64,
        )

        # A lightweight generic 3D head model (mm). Values are approximate.
        pts_3d = np.array(
            [
                [0.0, 0.0, 0.0],  # nose tip
                [0.0, -63.6, -12.5],  # chin
                [-43.3, 32.7, -26.0],  # left eye corner
                [43.3, 32.7, -26.0],  # right eye corner
                [-28.9, -28.9, -24.1],  # left mouth corner
                [28.9, -28.9, -24.1],  # right mouth corner
            ],
            dtype=np.float64,
        )

        focal = image_w
        cam_matrix = np.array(
            [
                [focal, 0, image_w / 2],
                [0, focal, image_h / 2],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )

        dist = np.zeros((4, 1))
        ok, rvec, tvec = cv2.solvePnP(pts_3d, pts_2d, cam_matrix, dist, flags=cv2.SOLVEPNP_ITERATIVE)

        if not ok:
            return 0.0, 0.0, 0.0

        R, _ = cv2.Rodrigues(rvec)
        sy = np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
        singular = sy < 1e-6

        if not singular:
            yaw = np.degrees(np.arctan2(R[2, 1], R[2, 2]))
            pitch = np.degrees(np.arctan2(-R[2, 0], sy))
            roll = np.degrees(np.arctan2(R[1, 0], R[0, 0]))
        else:
            yaw = np.degrees(np.arctan2(-R[1, 2], R[1, 1]))
            pitch = np.degrees(np.arctan2(-R[2, 0], sy))
            roll = 0

        return float(yaw), float(pitch), float(roll)

    def _bbox_from_landmarks(
        self, landmarks, w: int, h: int, pad_ratio: float | None = None
    ) -> Tuple[int, int, int, int]:
        xs = [lm.x * w for lm in landmarks]
        ys = [lm.y * h for lm in landmarks]
        x1, y1 = max(0, int(min(xs))), max(0, int(min(ys)))
        x2, y2 = min(w - 1, int(max(xs))), min(h - 1, int(max(ys)))

        # expand a bit
        pad = int((pad_ratio or self.pad_ratio) * max(w, h))
        x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
        x2, y2 = min(w - 1, x2 + pad), min(h - 1, y2 + pad)

        return x1, y1, x2 - x1 + 1, y2 - y1 + 1

    def _relative_bbox_to_abs(self, rel_bbox, w: int, h: int) -> Tuple[int, int, int, int]:
        x = int(rel_bbox.xmin * w)
        y = int(rel_bbox.ymin * h)
        bw = int(rel_bbox.width * w)
        bh = int(rel_bbox.height * h)
        return self._clip_bbox((x, y, bw, bh), w, h)

    @staticmethod
    def _clip_bbox(bbox: Tuple[int, int, int, int], w: int, h: int) -> Tuple[int, int, int, int]:
        x, y, bw, bh = bbox
        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        bw = max(1, min(bw, w - x))
        bh = max(1, min(bh, h - y))
        return x, y, bw, bh

    def _expand_bbox(
        self, bbox: Tuple[int, int, int, int], w: int, h: int, pad_ratio: float | None = None
    ) -> Tuple[int, int, int, int]:
        x, y, bw, bh = bbox
        pad = int((pad_ratio or self.pad_ratio) * max(bw, bh))
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(w, x + bw + pad)
        y2 = min(h, y + bh + pad)
        return self._clip_bbox((x1, y1, x2 - x1, y2 - y1), w, h)

    @staticmethod
    def _iou(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> float:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        ax2, ay2 = ax + aw, ay + ah
        bx2, by2 = bx + bw, by + bh

        inter_x1 = max(ax, bx)
        inter_y1 = max(ay, by)
        inter_x2 = min(ax2, bx2)
        inter_y2 = min(ay2, by2)

        if inter_x1 >= inter_x2 or inter_y1 >= inter_y2:
            return 0.0

        inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
        union_area = aw * ah + bw * bh - inter_area
        return inter_area / union_area if union_area else 0.0

    def estimate(self, bgr_image: np.ndarray) -> List[Dict]:
        h, w = bgr_image.shape[:2]
        rgb = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        mesh_res = self._mesh.process(rgb)
        rgb.flags.writeable = True
        det_res = self._detector.process(rgb)

        faces = []

        detection_bboxes: List[Tuple[Tuple[int, int, int, int], float]] = []
        if det_res and det_res.detections:
            for det in det_res.detections:
                rel_bbox = det.location_data.relative_bounding_box
                bbox = self._relative_bbox_to_abs(rel_bbox, w, h)
                score = float(det.score[0]) if det.score else 0.5
                detection_bboxes.append((bbox, score))

        if mesh_res and mesh_res.multi_face_landmarks:
            for face_lms in mesh_res.multi_face_landmarks:
                lms = face_lms.landmark
                yaw, pitch, roll = self._get_head_pose(lms, w, h)

                att_yaw = max(0.0, 1.0 - abs(yaw) / self.yaw_ok)
                att_pitch = max(0.0, 1.0 - abs(pitch) / self.pitch_ok)
                attention = float(att_yaw * att_pitch)

                # looking target
                if abs(yaw) <= self.yaw_ok and abs(pitch) <= self.pitch_ok:
                    target = "screen"
                else:
                    target = (
                        "left"
                        if yaw > self.yaw_ok
                        else "right"
                        if yaw < -self.yaw_ok
                        else "up"
                        if pitch < -self.pitch_ok
                        else "down"
                    )

                bbox = self._bbox_from_landmarks(lms, w, h)

                faces.append(
                    {
                        "bbox": bbox,
                        "yaw": yaw,
                        "pitch": pitch,
                        "roll": roll,
                        "attention": attention,
                        "looking_target": target,
                    }
                )

        # Add detections missed by the mesh (helps when landmarks fail)
        for det_bbox, det_score in detection_bboxes:
            if not any(self._iou(det_bbox, face["bbox"]) > 0.3 for face in faces):
                expanded = self._expand_bbox(det_bbox, w, h)
                faces.append(
                    {
                        "bbox": self._clip_bbox(expanded, w, h),
                        "yaw": 0.0,
                        "pitch": 0.0,
                        "roll": 0.0,
                        "attention": float(max(det_score, 0.4)),
                        "looking_target": "screen",
                    }
                )

        return faces

