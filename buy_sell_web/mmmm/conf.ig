# The data would be downloaded to this path
# Make sure you have approx 165GB space in this
# path to download the complete dataset.

# downloaded with get_testset.sh
destination='./'
# The subjects you want to download the train data for.
# Start with a few if all you want to do is examine the data
subjects=( Chenglei_studio)
# All subjects:
# subjects=(Chenglei_studio  Franzi_studio  Helge_outdoor  Nadia_outdoor  Natalia_outdoor  Oleks_outdoor  Oleks_studio  Pablo_outdoor  Simeng_moving_cam  Simeng_outdoor  Simeng_studio  Weipeng_outdoor  Weipeng_studio)

# We provide images, template meshes, camera calibration, results from 
# MonoPerfCap, as well as the ground truth for some of the sequences.
# Unset if you do NOT want to download the images, results or ground truth.
download_images=1
download_results=1
download_ground_truth=1
download_template_meshes = 1

# Set if you agree with the license conditions and want
# to proceed with downloading the dataset
ready_to_download=1
