#!/bin/bash
# Script to fetch the available data.  
# It uses config as the configuration file
echo "Reading configuration from ./config....." >&2
source ./conf.ig
if [[ $ready_to_download -eq 0 ]]; then
  echo "Please read the documentation and edit the config file accordingly." >&2
  exit 1
fi
if [ ! -d "$destination" ]; then
    mkdir "$destination"
fi

source_path="http://monoperfcap.mpi-inf.mpg.de/monoperfcap_dataset"
echo "Download destination set to $destination " >&2

for subject in ${subjects[@]}; do 
  if [ ! -d "$destination/$subject" ]; then
      mkdir "$destination/$subject"
  fi
  
  wget "$source_path/$subject/template.zip" -P "$destination/$subject"
  wget "$source_path/$subject/calib.txt" -P "$destination/$subject"
  
  if [ $download_images -ne 0 ]; then
      wget "$source_path/$subject/images.zip" -P "$destination/$subject"
  fi
  
  if [ $download_results -ne 0 ]; then
      wget "$source_path/$subject/result.zip" -P "$destination/$subject"
  fi
  
  if [ $download_ground_truth -ne 0  ] ; then
	  if [ "$subject" == "Chenglei_studio"  ] || [ "$subject" == "Helge_outdoor"  ] || [ "$subject" == "Pablo_outdoor"  ]; then
          wget "$source_path/$subject/ground_truth.zip" -P "$destination/$subject"
	  fi
  fi
  
 
done #Subject
