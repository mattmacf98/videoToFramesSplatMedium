import argparse
import os
import shutil

from MP4Processor import MP4Processor
from StructureFromMotionProcessor import StructureFromMotionProcessor


def main(mp4_path, output_folder, selected_folder, num_frames, gif_path, gif_fps):
    database_path = "database.db"
    colmap_executable_path = "COLMAP.app/Contents/MacOS/colmap"

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    if os.path.exists(selected_folder):
        shutil.rmtree(selected_folder)
    if os.path.exists(gif_path):
        os.remove(gif_path)
    if os.path.exists(database_path):
        os.remove(database_path)

    # process mp4
    mp4_processor = MP4Processor()
    all_frames = mp4_processor.split_video_to_frames(mp4_path, output_folder)
    selected_frames = mp4_processor.select_frames(all_frames, num_frames, output_folder, selected_folder)
    mp4_processor.create_gif(selected_frames, selected_folder, gif_path, gif_fps)

    # extract features
    structure_from_motion_processor = StructureFromMotionProcessor(colmap_executable_path)
    extract_features_success = structure_from_motion_processor.extract_features(selected_folder, database_path)
    if not extract_features_success:
        print("Failed extraction")
        return

    # match features
    match_features_success = structure_from_motion_processor.match_features(database_path)
    if not match_features_success:
        print("Matching failed")
        return

    # Bundle Adjustment
    bundle_adjustment_success = structure_from_motion_processor.bundle_mapper(selected_folder, database_path,
                                                                              "distorted/sparse/")
    if not bundle_adjustment_success:
        print("Bundle Adjustment Failed")
        return

    # Undistort Images
    undistort_images_success = structure_from_motion_processor.undistort_images(selected_folder, "distorted/sparse/0",
                                                                                "output/")
    if not undistort_images_success:
        print("Undistort Failed")
        return

    # Organize folder structure to match the expected structure for splatting
    os.makedirs("output/sparse/0", exist_ok=True)
    shutil.move("output/sparse/cameras.bin", "output/sparse/0/cameras.bin")
    shutil.move("output/sparse/images.bin", "output/sparse/0/images.bin")
    shutil.move("output/sparse/points3D.bin", "output/sparse/0/points3D.bin")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process video frames and create a GIF and a frame set.")

    parser.add_argument("input_video", help="Path to the input video file")
    parser.add_argument("all_frames_dir", help="Directory to store all frames")
    parser.add_argument("selected_frames_dir", help="Directory to store selected frames")
    parser.add_argument("frame_count", type=int, help="Number of frames to process")
    parser.add_argument("output_gif", help="Path to the output GIF file")
    parser.add_argument("fps", type=int, help="Frames per second for the output GIF")

    args = parser.parse_args()

    main(args.input_video, args.all_frames_dir, args.selected_frames_dir, args.frame_count, args.output_gif, args.fps)
