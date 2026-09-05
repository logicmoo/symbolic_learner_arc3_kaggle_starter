> [← Project README](../../README.md)

# Table of Contents

* [image\_codec](#image_codec)
  * [ARC\_PALETTE](#image_codec.ARC_PALETTE)
  * [PREFERRED\_KEYS](#image_codec.PREFERRED_KEYS)
  * [extract\_latest\_frame](#image_codec.extract_latest_frame)
  * [frame\_to\_image](#image_codec.frame_to_image)
  * [frame\_to\_png\_bytes](#image_codec.frame_to_png_bytes)
  * [save\_frame](#image_codec.save_frame)

<a id="image_codec"></a>

# image\_codec

<a id="image_codec.ARC_PALETTE"></a>

#### ARC\_PALETTE

<a id="image_codec.PREFERRED_KEYS"></a>

#### PREFERRED\_KEYS

<a id="image_codec.extract_latest_frame"></a>

#### extract\_latest\_frame

```python
def extract_latest_frame(*sources: Any) -> np.ndarray
```

<a id="image_codec.frame_to_image"></a>

#### frame\_to\_image

```python
def frame_to_image(frame: np.ndarray, scale: int = 10) -> Image.Image
```

<a id="image_codec.frame_to_png_bytes"></a>

#### frame\_to\_png\_bytes

```python
def frame_to_png_bytes(frame: np.ndarray, scale: int = 10) -> bytes
```

<a id="image_codec.save_frame"></a>

#### save\_frame

```python
def save_frame(frame: np.ndarray, path: str | Path, scale: int = 10) -> Path
```
