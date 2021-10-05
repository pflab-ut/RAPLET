# RAPLET -- ROS Architecture aware Publish/Subscribe Latency Evaluation Tool

## Build
```
make
```

## Run your app with RAPLET
(Optional) Terminal #1:
```
python3 kernel_info.py
```

Terminal #2 (After executing kernel_info.py):
```
LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libboost_system.so /path/to/lhook.so" roslaunch foo bar
```

## Visualize
TODO
