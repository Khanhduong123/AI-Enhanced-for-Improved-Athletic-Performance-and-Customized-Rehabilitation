```bash

├───ai_model_capstone
│   ├───checkpoints
│   │   ├───gcn
│   │   │   ├───finetune
│   │   │   └───pretrain
│   │   └───spoter
│   │       ├───finetune
│   │       └───pretrain
│   ├───config
│   ├───core
│   ├───data
│   │   ├───keypoints
│   │   │   ├───private_data
│   │   │   │   ├───train
│   │   │   │   │   ├───Happy_Baby_Pose
│   │   │   │   │   └───Head_To_Knee_Pose
│   │   │   │   └───val
│   │   │   │       ├───Happy_Baby_Pose
│   │   │   │       └───Head_To_Knee_Pose
│   │   │   └───public_data
│   │   │       ├───train
│   │   │       │   ├───Garland_Pose
│   │   │       │   ├───Happy_Baby_Pose
│   │   │       │   └───Head_To_Knee_Pose
│   │   │       └───val
│   │   │           ├───Garland_Pose
│   │   │           ├───Happy_Baby_Pose
│   │   │           └───Head_To_Knee_Pose
│   │   ├───processed_video
│   │   │   └───public_data
│   │   │       ├───train
│   │   │       │   ├───Garland_Pose
│   │   │       │   ├───Happy_Baby_Pose
│   │   │       │   ├───Head_To_Knee_Pose
│   │   │       │   ├───Lunge_Pose
│   │   │       │   ├───Mountain_Pose
│   │   │       │   ├───Plank_Pose
│   │   │       │   ├───Raised_Arms_Pose
│   │   │       │   ├───Seated_Forward_Bend
│   │   │       │   ├───Staff_Pose
│   │   │       │   └───Standing_Forward_Bend
│   │   │       └───val
│   │   │           ├───Garland_Pose
│   │   │           ├───Happy_Baby_Pose
│   │   │           ├───Head_To_Knee_Pose
│   │   │           ├───Lunge_Pose
│   │   │           ├───Mountain_Pose
│   │   │           ├───Plank_Pose
│   │   │           ├───Raised_Arms_Pose
│   │   │           ├───Seated_Forward_Bend
│   │   │           ├───Staff_Pose
│   │   │           ├───Standing_Forward_Bend
│   │   │           └───train
│   │   └───raw_video
│   │       ├───private_data
│   │       │   ├───train
│   │       │   └───val
│   │       └───public_data
│   │           ├───Garland_Pose
│   │           ├───Happy_Baby_Pose
│   │           ├───Head_To_Knee_Pose
│   │           ├───Lunge_Pose
│   │           ├───Mountain_Pose
│   │           ├───Plank_Pose
│   │           ├───Raised_Arms_Pose
│   │           ├───Seated_Forward_Bend
│   │           ├───Staff_Pose
│   │           └───Standing_Forward_Bend
│   ├───images
│   ├───notebook
│   └───summary
├───backend_capstone
│   ├───src
│   │   └───v1
│   │       ├───configs
│   │       │   └───checkpoints
│   │       │       ├───gcn
│   │       │       │   ├───finetune
│   │       │       │   └───pretrain
│   │       │       └───spoter
│   │       │           ├───finetune
│   │       │           └───pretrain
│   │       ├───models
│   │       ├───providers
│   │       ├───routers
│   │       └───services
│   └───temp_videos
└───frontend_capstone
```