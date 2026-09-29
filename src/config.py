import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Any, Self

import sounddevice
import tomli_w
from pydantic import BaseModel, BeforeValidator, ConfigDict


CONFIG_FOLDER = Path(__file__).parents[1] / ".config"
CONFIG_FILE: Path = CONFIG_FOLDER / "config.toml"

_BOARDS: Path = Path(__file__).parents[1] / "boards"
_TTS_VOICES: Path = Path(__file__).parents[1] / "tts_voices"


def force_absolute(base_dir: str | Path) -> Callable[[Any], Path]:
    """Pre-validator to turn relative paths into absolute paths."""
    # Easier to work with absolute everywhere by adding context to relative paths once
    def _validate(value: Any) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path

        return (Path(base_dir) / path).resolve()

    return _validate


BoardFile = Annotated[Path, BeforeValidator(force_absolute(_BOARDS))]
TTSFile = Annotated[Path, BeforeValidator(force_absolute(_TTS_VOICES))]


class DeviceInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    index: int
    hostapi: int
    max_input_channels: int
    max_output_channels: int
    default_low_input_latency: float
    default_low_output_latency: float
    default_high_input_latency: float
    default_high_output_latency: float
    default_samplerate: float

    @classmethod
    def get_devices(cls) -> list[Self]:
        """Returns all devices (both input and output) available"""
        return [cls.model_validate(device) for device in sounddevice.query_devices()]

    @classmethod
    def get_output_devices(cls) -> list[Self]:
        """Returns all output devices available """
        return [
            device for device in cls.get_devices() if device.max_output_channels > 0
        ]

    @classmethod
    def get_default_output_device(cls) -> Self | None:
        """Returns default output device if any"""
        try:
            return cls.model_validate(sounddevice.query_devices(kind="output"))
        except sounddevice.PortAudioError:
            return None

    @classmethod
    def from_device_name(cls, name: str) -> Self | None:
        return next((device for device in cls.get_output_devices() if device.name == name), None)


class ConfigFile(BaseModel):
    welcome_messages: tuple[str, ...] = (
        "welcome to B L A A C!",
        "Good luck with your conversation!",
        "Hey You, you've got this!",
    )
    default_speaker: str | None = None
    default_headphones: str | None = None

    home_board: BoardFile = Path("communikate-20")

    default_speaking_voice: TTSFile = Path("news.safetensors")
    default_feedback_voice: TTSFile = Path("news.safetensors")
    # warning: setting this value above 1 is possible but not recommended.
    expressiveness: float = 0.3
    # Setting the below value to true means that TTS phrases specific to your current voice
    # will take priority over audio clips that are not specific to your current voice.
    prioritise_tts_over_generic_audio: bool = False

    @classmethod
    def load(cls, path: Path = CONFIG_FILE) -> Self:
        """Loads config file (toml) from disc"""
        data = {}
        if path.exists():
            with path.open("rb") as f:
                data = tomllib.load(f)
        return cls.model_validate(data)

    def save(self, path: Path = CONFIG_FILE) -> None:
        """Saves config file (toml) to disc"""
        with open(path, "w") as file:
            file.write(tomli_w.dumps(self.model_dump(mode="json", exclude_none=True)))


class Config(BaseModel):
    welcome_messages: tuple[str, ...]
    default_speaker: DeviceInfo
    default_headphones: DeviceInfo

    home_board: BoardFile

    default_speaking_voice: TTSFile
    default_feedback_voice: TTSFile
    expressiveness: float
    prioritise_tts_over_generic_audio: bool

    def into_config_file(self) -> ConfigFile:
        """Casts programme config into config file object"""
        # assuming all programme config should be saved
        return ConfigFile(
            default_headphones=self.default_headphones.name,
            default_speaker=self.default_speaker.name,
            welcome_messages=self.welcome_messages,
            home_board=self.home_board,
            default_speaking_voice=self.default_speaking_voice,
            default_feedback_voice=self.default_feedback_voice,
            expressiveness=self.expressiveness,
            prioritise_tts_over_generic_audio=self.prioritise_tts_over_generic_audio
        )

