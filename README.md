# RAPLET -- ROS Architecture aware Publish/Subscribe Latency Evaluation Tool

## Build
```
make
```

## Run your app with RAPLET
Terminal #1:
```
python3 kernel_info.py
```

Terminal #2 (After executing kernel_info.py):
```
LD_PRELOAD=/path/to/lhook.so rosrun foo bar
```

## Visualize
TODO
