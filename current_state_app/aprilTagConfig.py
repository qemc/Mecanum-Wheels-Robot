from pupil_apriltags import Detector
import warnings

class AprilTagConfig:
    def __init__(self, tag_family='tag36h11', nthreads=4, quad_decimate=1.0,
                 quad_sigma=1.0, refine_edges=1, decode_sharpening=0.25,
                 debug=0, tag_size=0.08, correction_factor=1.1):
        self.tag_size = tag_size
        self.correction_factor = correction_factor
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.detector = Detector(
                
                families=tag_family,
                nthreads=nthreads,
                quad_decimate=quad_decimate,
                quad_sigma=quad_sigma,
                refine_edges=refine_edges,
                decode_sharpening=decode_sharpening,
                debug=debug
                
            )

    def get_detector(self): return self.detector
    def get_tag_size(self): return self.tag_size
    def get_correction_factor(self): return self.correction_factor