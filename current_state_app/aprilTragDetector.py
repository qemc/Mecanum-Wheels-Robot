import cv2
import warnings
from aprilTagConfig import AprilTagConfig
from mathUtils import calculate_2d_position, calculate_yaw_angle

class AprilTagDetector:
    def __init__(self, camera_matrix, tag_config=None):
        """
        Initializes the AprilTagDetector.
        Args:
            camera_matrix (np.array): Camera intrinsic matrix.
            tag_config (AprilTagConfig): Configuration for AprilTag detection.
        """
        self.camera_matrix = camera_matrix
        self.tag_config = tag_config if tag_config else AprilTagConfig()
        self.detector = self.tag_config.get_detector()
        self.tag_size = self.tag_config.get_tag_size()
        self.correction_factor = self.tag_config.get_correction_factor()
        warnings.filterwarnings('ignore', message='.*more than one new minima found.*')

    def detect_tags(self, frame):
        """
        Detects AprilTags in the given frame.
        Args:
            frame (np.array): The input image/frame in which to detect tags.
        Returns:
            list: A list of detected AprilTags with their pose information.
        """
        if frame is None:
            return []
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        tags = self.detector.detect(
            
            gray,
            estimate_tag_pose=True,
            camera_params=[
                self.camera_matrix[0, 0], self.camera_matrix[1, 1],
                self.camera_matrix[0, 2], self.camera_matrix[1, 2]
            ],
            tag_size=self.tag_size
        )
        
        # unique_tags = []
        # seen_ids = set()
        
        # for tag in tags:
        #     if tag.tag_id not in seen_ids:
        #         unique_tags.append(tag)
        #         seen_ids.add(tag.tag_id)
    
        # return unique_tags

        return tags
    
    def get_pose_data(self, tags):
        """Calculate pose data from detected tags."""
        pose_data = []
        
        for tag in tags:
            
            try:
                x_cm, y_cm = calculate_2d_position(tag.pose_t, self.correction_factor)
                
                angle = 1 #calculate_yaw_angle(tag.pose_R)
                if angle is not None:
                    pose_data.append({
                        "id": tag.tag_id,
                        "x_cm": x_cm,
                        "y_cm": y_cm,
                        "Yaw": angle
                    })
            except Exception as e:
                print(f"Error calculating pose for tag {tag.tag_id}: {str(e)}")
                continue
        return pose_data

    def draw_tags(self, frame, tags):
        """
        Draws detected tags and their poses on the frame.
        Args:
            frame (np.array): The frame to draw on.
            tags (list): A list of detected AprilTags.
        """
        for tag in tags:
            
            corners = tag.corners.astype(int)
            center = tuple(tag.center.astype(int))

            x_cm, y_cm = calculate_2d_position(tag.pose_t, self.correction_factor)
            angle = 1 # calculate_yaw_angle(tag.pose_R)

            # Draw tag center and outline
            cv2.circle(frame, center, 5, (0, 255, 0), -1)
            cv2.polylines(frame, [corners.reshape((-1, 1, 2))], True, (0, 255, 0), 2)

            # Add text for tag ID and pose
            text = f"ID:{tag.tag_id} X:{x_cm:.1f} Y:{y_cm:.1f} R:{angle:.1f}"
            text_pos = (center[0] - 10, center[1] - 10)
            cv2.putText(frame, text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)