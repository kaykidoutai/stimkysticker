from __future__ import annotations

import time
import typing
from pathlib import Path

from attr import dataclass


@dataclass
class User:
    # The amount of seconds the user has banked
    time_bank: float
    # The cost of each sticker in seconds
    sticker_cost: float
    # The max number of stickers a user can accrue
    max_stickers: int
    # The last we checked the bank
    last_checked_time: float
    # All the images that printed
    printed_images: typing.List[Path]

    @property
    def maxed_time_bank(self) -> bool:
        self.update_time_bank()
        return self.time_bank > (self.max_stickers * self.sticker_cost)

    @property
    def stickers_remaining(self):
        self.update_time_bank()
        if self.maxed_time_bank:
            return self.max_stickers
        return int(self.time_bank / self.sticker_cost)

    def use_sticker(self, image_printed: Path):
        self.update_time_bank()
        if self.stickers_remaining:
            if self.maxed_time_bank:
                self.time_bank = (
                    self.max_stickers * self.sticker_cost
                ) - self.sticker_cost
            else:
                self.time_bank -= self.sticker_cost
            self.printed_images.append(image_printed)

    def update_time_bank(self):
        self.time_bank += time.time() - self.last_checked_time
        self.last_checked_time = time.time()

    @classmethod
    def new_user(cls, max_stickers: int, sticker_cost: float) -> User:
        return User(
            time_bank=max_stickers * sticker_cost,
            sticker_cost=sticker_cost,
            max_stickers=max_stickers,
            last_checked_time=time.time(),
            printed_images=[],
        )

    @property
    def remaining_stickers_str(self) -> str:
        self.update_time_bank()
        if self.stickers_remaining:
            retstr = (
                f"You have {self.stickers_remaining} remaining sticker"
                f"{'s' if self.stickers_remaining > 1 else ''}. "
            )
        else:
            retstr = f"You have no stickers remaining :( "
        return (
            f"{retstr}\nStickers recharge at a rate of 1 sticker every {self.sticker_cost} seconds "
            f"(up to {self.max_stickers} max)"
        )

    @property
    def user_info(self) -> str:
        self.update_time_bank()
        return (
            f"You've printed {len(self.printed_images)} sticker{'s' if self.stickers_remaining > 1 else ''}.\n"
            f"{self.remaining_stickers_str}"
        )
