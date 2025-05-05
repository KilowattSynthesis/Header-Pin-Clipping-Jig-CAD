import itertools
from dataclasses import dataclass
from pathlib import Path

import build123d as bd
import build123d_ease as bde
from build123d_ease import show
from loguru import logger


@dataclass
class ClipJigSpec:
    """Specification for clip_jig."""

    pin_pitch: float = 2.54
    pin_count_x: int = 8
    pin_count_y: int = 3

    pin_hole_size: float = 1.5

    # ESQ-126-13-G-D - Length B = 7.37mm
    # PCB is 1.6mm thick
    # Difference is 5.77mm
    target_pin_length: float = 5.4

    def __post_init__(self) -> None:
        """Post initialization checks."""

    def total_x(self) -> float:
        """Total x dimension."""
        return self.pin_pitch * (self.pin_count_x - 1)

    def total_y(self) -> float:
        """Total y dimension."""
        return self.pin_pitch * (self.pin_count_y)


def make_clip_jig(spec: ClipJigSpec) -> bd.Part | bd.Compound:
    """Create a CAD model of clip_jig."""
    p = bd.Part(None)

    p += bd.Box(
        spec.total_x(),
        spec.total_y(),
        spec.target_pin_length,
        align=bde.align.ANCHOR_BOTTOM,
    )

    # Create pin holes
    for pin_x, pin_y in itertools.product(
        bde.evenly_space_with_center(
            count=spec.pin_count_x, spacing=spec.pin_pitch
        ),
        bde.evenly_space_with_center(
            count=spec.pin_count_y, spacing=spec.pin_pitch
        ),
    ):
        p -= bd.Cylinder(
            radius=spec.pin_hole_size / 2,
            height=spec.target_pin_length,
            align=bde.align.ANCHOR_BOTTOM,
        ).translate((pin_x, pin_y, 0))

    return p


if __name__ == "__main__":
    parts = {
        "clip_jig": show(make_clip_jig(ClipJigSpec())),
        "clip_jig_big_holes": show(
            make_clip_jig(ClipJigSpec(pin_hole_size=2))
        ),
    }

    logger.info("Showing CAD model(s)")

    (export_folder := Path(__file__).parent.with_name("build")).mkdir(
        exist_ok=True
    )
    for name, part in parts.items():
        assert isinstance(part, bd.Part | bd.Solid | bd.Compound), (
            f"{name} is not an expected type ({type(part)})"
        )

        bd.export_stl(part, str(export_folder / f"{name}.stl"))
        bd.export_step(part, str(export_folder / f"{name}.step"))
