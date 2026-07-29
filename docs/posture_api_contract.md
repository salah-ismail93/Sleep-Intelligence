# Posture API Contract

## Endpoint

`POST /posture`

Version 1 is stateless. Every request supplies both the current orientation and
the calibration reference; the service does not store calibration data.

## Request

The request contains two quaternions:

- `q_reference`: the orientation recorded during supine calibration.
- `q_current`: the current wearable orientation.

Each quaternion is represented as a JSON object with the named fields `w`, `x`,
`y`, and `z`.

The quaternions represent rotations from the world frame to the device frame.
For a correctly mounted chest wearable, the right-handed device axes are:

- `+X`: toward the patient's right.
- `+Y`: toward the patient's head.
- `+Z`: outward from the chest.

The relative orientation is:

`q_relative = q_current ⊗ q_reference⁻¹`

The rightmost rotation is applied first. Therefore, `q_relative` maps the
calibrated device frame to the current device frame. Only this relative
orientation is passed to the posture classifier.

## Validation and Normalization

Every quaternion component must be a finite number.

The norm of both `q_reference` and `q_current` must be within the inclusive
range `[0.95, 1.05]`. Accepted quaternions are always normalized to unit length
before the relative orientation is calculated.

The request is rejected with an HTTP validation error, and classification is
not attempted, if either quaternion:

- Is malformed.
- Contains a non-finite component.
- Has a norm outside `[0.95, 1.05]`.
- Cannot be normalized, including a zero-norm quaternion.

Invalid input must not produce the `unknown` posture label.

## Response

The response contains:

- `posture`: one of `supine`, `prone`, `left_side`, `right_side`, or `unknown`.
- `confidence`: a number in the inclusive range `[0.0, 1.0]` representing the
  classifier's confidence in the returned label.

For a supported posture, higher confidence means the relative orientation falls
more clearly within that posture's confidence region.

For `unknown`, higher confidence means the classifier is more confident that
the valid relative orientation cannot be safely assigned to a supported
posture. This can occur when the orientation falls outside every defined
confidence region or lies within an ambiguous decision boundary.

The classifier must not force an uncertain valid orientation into one of the
four supported posture labels.

## Calibration and State

The client performs a short calibration while the patient lies supine with the
wearable correctly mounted. The resulting quaternion is sent as `q_reference`
with every request.

The service does not persist calibrations in Version 1. Persistent calibration
records may be introduced later alongside authenticated users, registered
devices, and durable storage.
