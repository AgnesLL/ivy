from typing import Optional, Union

# global
import numpy as np

# local
import ivy
from ivy.functional.backends.numpy.helpers import _scalar_output_to_0d_array
from ivy.func_wrapper import with_unsupported_dtypes
from . import backend_version


def logit(
    x: np.ndarray,
    /,
    *,
    eps: Optional[float] = None,
    out: Optional[np.ndarray] = None,
):
    x_dtype = x.dtype
    if eps is None:
        x = np.where(np.logical_or(x > 1, x < 0), np.nan, x)
    else:
        x = np.clip(x, eps, 1 - eps)
    ret = (np.log(x / (1 - x))).astype(x_dtype)
    if np.isscalar(ret):
        return np.array(ret)
    return ret


@_scalar_output_to_0d_array
def thresholded_relu(
    x: np.ndarray,
    /,
    *,
    threshold: Union[int, float] = 0,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    x, threshold = ivy.promote_types_of_inputs(x, threshold)
    return np.where(x > threshold, x, 0).astype(x.dtype)


thresholded_relu.support_native_out = True


@_scalar_output_to_0d_array
def relu6(x: np.ndarray, /, *, out: Optional[np.ndarray] = None) -> np.ndarray:
    return np.minimum(np.maximum(x, 0, dtype=x.dtype), 6, out=out, dtype=x.dtype)


relu6.support_native_out = True


def batch_norm(
    x: np.ndarray,
    mean: np.ndarray,
    variance: np.ndarray,
    /,
    *,
    scale: Optional[np.ndarray] = None,
    offset: Optional[np.ndarray] = None,
    training: bool = False,
    eps: float = 1e-5,
):
    ndims = len(x.shape)
    if training:
        dims = (0, *range(2, ndims))
        mean = np.mean(x, axis=dims)
        variance = np.var(x, axis=dims)
    x = np.transpose(x, (0, *range(2, ndims), 1))
    inv = 1.0 / np.sqrt(variance + eps)
    if scale is not None:
        inv *= scale
    ret = x * inv.astype(x.dtype, copy=False) + (
        offset - mean * inv if offset is not None else -mean * inv
    ).astype(x.dtype)
    return np.transpose(ret, (0, ndims - 1, *range(1, ndims - 1)))


@with_unsupported_dtypes({"1.23.0 and below": ("bool",)}, backend_version)
@_scalar_output_to_0d_array
def logsigmoid(input: np.ndarray) -> np.ndarray:
    return -(np.log1p(np.exp(-(input))))


@_scalar_output_to_0d_array
def selu(x: np.ndarray, /, *, out: Optional[np.ndarray] = None) -> np.ndarray:
    alpha = 1.6732632423543772848170429916717
    scale = 1.0507009873554804934193349852946
    ret = (scale * np.where(x > 0, x, alpha * np.expm1(x))).astype(x.dtype)
    if ivy.exists(out):
        return ivy.inplace_update(out, ret).astype(x.dtype)
    return ret


selu.support_native_out = True
