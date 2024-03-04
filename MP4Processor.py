import os
import shutil
import subprocess


class MP4Processor:
    def split_video_to_frames(selfself, mp4_path, output_folder):

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        subprocess.run(['ffmpeg', '-i', mp4_path, '-q:v', '2', os.path.join(output_folder, 'frame_%04d.jpg')])

        return os.listdir(output_folder)

    def select_frames(self, all_frames, num_frames, source_folder, selected_folder):
        total_frames = len(all_frames)
        sorted_all_frames = sorted(all_frames)

        step = max(total_frames // num_frames, 1)

        selected_frames = [f for i, f in enumerate(sorted_all_frames) if i % step == 0]
        selected_frames = selected_frames[:num_frames]

        if not os.path.exists(selected_folder):
            os.makedirs(selected_folder)

        for i, frame in enumerate(selected_frames):
            shutil.copy(os.path.join(source_folder, frame), os.path.join(selected_folder, 'frame_{:04d}.jpg'.format(i + 1)))

        return ['frame_{:04d}.jpg'.format(i + 1) for i in range(len(selected_frames))]

    def create_gif(self, selected_frames, selected_folder, gif_path, fps=30):
        list_file_path = os.path.join(selected_folder, 'frame_list.txt')
        with open(list_file_path, 'w') as f:
            for frame in selected_frames:
                f.write(f"file '{frame}'\n")

        # Use ffmpeg to create the GIF
        subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file_path, '-vf', f'fps={fps}', gif_path])

        # Remove the temporary list file
        os.remove(list_file_path)
