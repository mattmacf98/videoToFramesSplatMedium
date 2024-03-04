import os
import shutil


class StructureFromMotionProcessor:
    def __init__(self, colmap_executable_path):
        self.colmap_executable_path = colmap_executable_path

    def extract_features(self, image_folder_path, database_path, camera="OPENCV"):
        ## Feature extraction
        feat_extraction_cmd = self.colmap_executable_path + " feature_extractor " \
                                              "--database_path " + database_path + " \
                --image_path " + image_folder_path + " \
                --ImageReader.single_camera 1 \
                --ImageReader.camera_model " + camera + " \
                --SiftExtraction.use_gpu 1"
        exit_code = os.system(feat_extraction_cmd)
        return exit_code == 0

    # TODO: use sequential matching since it is a video
    def match_features(self, database_path):
        ## Feature matching
        feat_matching_cmd = self.colmap_executable_path + " exhaustive_matcher " \
                                              "--database_path " + database_path + " \
                --SiftMatching.use_gpu 1"
        exit_code = os.system(feat_matching_cmd)
        return exit_code == 0

    # TODO: see if I can update the tolerance value to make run faster
    def bundle_mapper(self, image_folder_path, database_path, output_folder_path):
        ## bundle mapper
        os.makedirs(output_folder_path, exist_ok=True)
        mapper_cmd = (self.colmap_executable_path + " mapper \
                --database_path " + database_path + " \
                --image_path " + image_folder_path + " \
                --output_path " + output_folder_path)
        exit_code = os.system(mapper_cmd)
        return exit_code == 0

    def undistort_images(self, image_folder_path, distorted_sparse_folder_path, output_folder_path):
        ### undistort images
        os.makedirs(output_folder_path, exist_ok=True)
        shutil.rmtree(output_folder_path)
        img_undist_cmd = (self.colmap_executable_path + " image_undistorter \
            --image_path " + image_folder_path + " \
            --input_path " + distorted_sparse_folder_path + " \
            --output_path " + output_folder_path + "\
            --output_type COLMAP")
        exit_code = os.system(img_undist_cmd)
        return exit_code == 0
