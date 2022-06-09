from enum import Enum

ARMOR_PREFIX = "Armor"
BODY_PREFIX = "Body"


class TitanAnatomy(Enum):
    HEAD = "Head"
    TORSO = "ChestUpper"
    SHOULDER_RIGHT = "ArmUpperRight"
    SHOULDER_LEFT = "ArmUpperLeft"
    HAND_RIGHT = "HandRight"
    HAND_LEFT = "HandLeft"
    LEG_RIGHT = "LegUpperRight"
    LEG_LEFT = "LegUpperLeft"

    ARM_RIGHT = (SHOULDER_RIGHT, HAND_RIGHT)
    ARM_LEFT = (SHOULDER_LEFT, HAND_LEFT)

    ARMS = (*ARM_RIGHT, *ARM_LEFT)

    LEGS = (LEG_RIGHT, LEG_LEFT)


TITAN_PARTS_ATOMIC = (
    TitanAnatomy.HEAD,
    TitanAnatomy.TORSO,
    TitanAnatomy.SHOULDER_RIGHT,
    TitanAnatomy.SHOULDER_LEFT,
    TitanAnatomy.HAND_RIGHT,
    TitanAnatomy.HAND_LEFT,
    TitanAnatomy.LEG_RIGHT,
    TitanAnatomy.LEG_LEFT,
)

TITAN_PARTS_CONSOLIDATED = (
    TitanAnatomy.HEAD,
    TitanAnatomy.TORSO,
    TitanAnatomy.ARMS,
    TitanAnatomy.LEGS,
)

TITAN_PARTS_ALL = (
    *TITAN_PARTS_ATOMIC,

    TitanAnatomy.ARMS,
    TitanAnatomy.LEGS,
)

TITAN_PART_REPRS = {
    TitanAnatomy.HEAD: "Head",
    TitanAnatomy.TORSO: "Torso",
    TitanAnatomy.SHOULDER_RIGHT: "Right Shoulder",
    TitanAnatomy.SHOULDER_LEFT: "Left Shoulder",
    TitanAnatomy.HAND_RIGHT: "Right Hand",
    TitanAnatomy.HAND_LEFT: "Left Hand",
    TitanAnatomy.LEG_RIGHT: "Right Leg",
    TitanAnatomy.LEG_LEFT: "Left Leg",

    TitanAnatomy.ARM_RIGHT: "Right Arm",
    TitanAnatomy.ARM_LEFT: "Left Arm",
    TitanAnatomy.ARMS: "Arms",
    TitanAnatomy.LEGS: "Legs"
}

TITAN_ANATOMY = {
    titan_part: {
        "armor": f"{ARMOR_PREFIX}{titan_part}",
        "body": f"{BODY_PREFIX}{titan_part}"
    }
    for titan_part
    in TITAN_PARTS_ATOMIC
}
