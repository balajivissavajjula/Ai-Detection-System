# ============================================================
# AI EXAM SURVEILLANCE SYSTEM V2
# CAMERA MODULE
# ============================================================

import cv2
import time
import threading
import numpy as np

import config


# ============================================================
# CAMERA CLASS
# ============================================================

class Camera:

    def __init__(self):

        self.source = config.get_camera_source()

        self.cap = None

        self.running = False
        self.connected = False

        self.frame_count = 0

        self.last_frame = None
        self.last_frame_time = 0.0

        self.lock = threading.RLock()
        self.thread = None

        self.last_error = ""

        self.reconnect_delay = 2.0
        self.read_error_delay = 0.10
        self.last_reconnect_time = 0.0

        self.failed_reads = 0
        self.reconnect_count = 0


    # ========================================================
    # OPEN CAMERA
    # ========================================================

    def open(self):

        with self.lock:

            # ------------------------------------------------
            # Already opened
            # ------------------------------------------------

            if self.cap is not None:

                try:

                    if self.cap.isOpened():

                        self.connected = True
                        self.last_error = ""

                        return True

                except Exception:
                    pass


            # ------------------------------------------------
            # Release stale capture
            # ------------------------------------------------

            if self.cap is not None:

                try:
                    self.cap.release()
                except Exception:
                    pass

                self.cap = None


            # ------------------------------------------------
            # Refresh source
            # ------------------------------------------------

            try:
                self.source = config.get_camera_source()
            except Exception:
                pass


            print()
            print("=" * 60)
            print("OPENING CAMERA")
            print("=" * 60)
            print("Source:", self.source)


            # ------------------------------------------------
            # Open VideoCapture
            # ------------------------------------------------

            try:

                self.cap = cv2.VideoCapture(self.source)

            except Exception as e:

                self.cap = None
                self.connected = False
                self.last_error = str(e)

                print("CAMERA OPEN ERROR:", e)

                return False


            # ------------------------------------------------
            # Check capture object
            # ------------------------------------------------

            try:

                opened = self.cap.isOpened()

            except Exception:

                opened = False


            if not opened:

                self.connected = False

                self.last_error = (
                    "Camera could not be opened"
                )

                print(
                    "CAMERA ERROR:",
                    self.last_error
                )

                try:
                    self.cap.release()
                except Exception:
                    pass

                self.cap = None

                return False


            # ------------------------------------------------
            # Buffer size
            # ------------------------------------------------

            try:

                self.cap.set(
                    cv2.CAP_PROP_BUFFERSIZE,
                    1
                )

            except Exception:
                pass


            # ------------------------------------------------
            # Resolution
            # ------------------------------------------------

            try:

                width = int(
                    getattr(
                        config,
                        "CAMERA_WIDTH",
                        640
                    )
                )

                height = int(
                    getattr(
                        config,
                        "CAMERA_HEIGHT",
                        480
                    )
                )

                self.cap.set(
                    cv2.CAP_PROP_FRAME_WIDTH,
                    width
                )

                self.cap.set(
                    cv2.CAP_PROP_FRAME_HEIGHT,
                    height
                )

            except Exception:
                pass


            # ------------------------------------------------
            # FPS
            # ------------------------------------------------

            try:

                self.cap.set(
                    cv2.CAP_PROP_FPS,
                    20
                )

            except Exception:
                pass


            # ------------------------------------------------
            # Initial connection state
            # ------------------------------------------------

            self.connected = True

            self.last_error = ""
            self.failed_reads = 0
            self.last_reconnect_time = time.time()


            print(
                "Camera opened successfully."
            )

            print(
                "Source:",
                self.source
            )

            print("=" * 60)

            return True


    # ========================================================
    # START CAMERA
    # ========================================================

    def start(self):

        with self.lock:

            if self.running:
                return True


            if not self.open():

                print(
                    "Camera start failed."
                )

                return False


            self.running = True


            self.thread = threading.Thread(

                target=self._capture_loop,

                name="CameraCaptureThread",

                daemon=True

            )

            self.thread.start()


            print(
                "Camera capture thread started."
            )

            return True


    # ========================================================
    # CAPTURE LOOP
    # ========================================================

    def _capture_loop(self):

        while self.running:

            with self.lock:
                cap = self.cap


            # ------------------------------------------------
            # No capture object
            # ------------------------------------------------

            if cap is None:

                self.connected = False

                self._try_reconnect()

                continue


            # ------------------------------------------------
            # Read frame
            # ------------------------------------------------

            try:

                success, frame = cap.read()

            except Exception as e:

                success = False
                frame = None

                self.last_error = str(e)


            # ------------------------------------------------
            # Failed frame
            # ------------------------------------------------

            if not success or frame is None:

                self.failed_reads += 1

                self.connected = False


                if not self.last_error:

                    self.last_error = (
                        "Failed to read camera frame"
                    )


                if self.failed_reads >= 5:

                    self._reconnect()

                else:

                    time.sleep(
                        self.read_error_delay
                    )

                continue


            # ------------------------------------------------
            # SUCCESSFUL FRAME
            # ------------------------------------------------

            self.failed_reads = 0

            self.connected = True

            self.last_error = ""


            with self.lock:

                self.last_frame = frame

                self.frame_count += 1

                self.last_frame_time = time.time()


    # ========================================================
    # RECONNECT CHECK
    # ========================================================

    def _try_reconnect(self):

        now = time.time()

        if (
            now - self.last_reconnect_time
            < self.reconnect_delay
        ):

            time.sleep(0.10)

            return


        self._reconnect()


    # ========================================================
    # RECONNECT
    # ========================================================

    def _reconnect(self):

        if not self.running:
            return


        now = time.time()


        if (
            now - self.last_reconnect_time
            < self.reconnect_delay
        ):

            time.sleep(0.10)

            return


        self.last_reconnect_time = now


        print(
            "Attempting camera reconnect..."
        )


        with self.lock:

            if self.cap is not None:

                try:
                    self.cap.release()
                except Exception:
                    pass

                self.cap = None

            self.connected = False


        time.sleep(
            self.reconnect_delay
        )


        if not self.running:
            return


        if self.open():

            self.reconnect_count += 1

            self.failed_reads = 0

            print(
                "Camera reconnect successful."
            )

        else:

            print(
                "Camera reconnect failed."
            )


    # ========================================================
    # GET FRAME
    # ========================================================

    def get_frame(self):

        if not self.running:

            self.start()


        with self.lock:

            if self.last_frame is None:
                return None

            return self.last_frame.copy()


    # ========================================================
    # CONNECTION STATUS
    # ========================================================

    def is_connected(self):

        try:

            with self.lock:

                if not self.running:
                    return False

                if self.cap is None:
                    return False

                try:

                    opened = bool(
                        self.cap.isOpened()
                    )

                except Exception:

                    opened = False


                if not opened:
                    return False


                # --------------------------------------------
                # IMPORTANT:
                # A successful recent frame proves that
                # the stream is actually alive.
                # --------------------------------------------

                if self.last_frame_time > 0:

                    age = (
                        time.time()
                        - self.last_frame_time
                    )

                    if age <= 5.0:

                        return True


                # --------------------------------------------
                # If camera is opened but no frame has been
                # received yet, use internal connection state.
                # --------------------------------------------

                return bool(self.connected)

        except Exception:

            return False


    # ========================================================
    # CAMERA STATUS
    # ========================================================

    def get_status(self):

        with self.lock:

            connected = self.is_connected()

            return {

                "connected":
                    connected,

                "running":
                    bool(self.running),

                "frames":
                    int(self.frame_count),

                "source":
                    self.source,

                "last_error":
                    self.last_error,

                "last_frame_time":
                    self.last_frame_time,

                "failed_reads":
                    self.failed_reads,

                "reconnects":
                    self.reconnect_count,

            }


    # ========================================================
    # RELEASE
    # ========================================================

    def release(self):

        print(
            "Releasing camera..."
        )


        self.running = False


        thread = self.thread


        if thread is not None:

            try:

                if (
                    thread.is_alive()
                    and
                    thread is not threading.current_thread()
                ):

                    thread.join(
                        timeout=2.0
                    )

            except Exception:
                pass


        with self.lock:

            if self.cap is not None:

                try:
                    self.cap.release()
                except Exception as e:

                    print(
                        "Camera release error:",
                        e
                    )

                self.cap = None


            self.connected = False

            self.last_frame = None

            self.last_frame_time = 0.0


        self.thread = None


        print(
            "Camera released."
        )


# ============================================================
# GLOBAL CAMERA INSTANCE
# ============================================================

camera = Camera()


# ============================================================
# ERROR FRAME
# ============================================================

def create_camera_error_frame(message):

    width = int(
        getattr(
            config,
            "CAMERA_WIDTH",
            640
        )
    )

    height = int(
        getattr(
            config,
            "CAMERA_HEIGHT",
            480
        )
    )


    frame = np.full(

        (
            height,
            width,
            3
        ),

        30,

        dtype=np.uint8

    )


    cv2.putText(

        frame,

        str(message),

        (40, height // 2),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.80,

        (255, 255, 255),

        2,

        cv2.LINE_AA

    )


    try:

        source_text = (
            f"Source: {camera.source}"
        )

        cv2.putText(

            frame,

            source_text,

            (40, height // 2 + 40),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.45,

            (180, 180, 180),

            1,

            cv2.LINE_AA

        )

    except Exception:
        pass


    return frame


# ============================================================
# JPEG ENCODER
# ============================================================

def encode_frame(frame, quality=80):

    try:

        success, encoded = cv2.imencode(

            ".jpg",

            frame,

            [
                int(
                    cv2.IMWRITE_JPEG_QUALITY
                ),
                int(quality),
            ]

        )


        if not success:
            return None


        return encoded.tobytes()


    except Exception as e:

        print(
            "JPEG encode error:",
            e
        )

        return None


# ============================================================
# GENERATE MJPEG FRAMES
# ============================================================

def generate_frames():

    try:

        from detector import detect

    except Exception as e:

        print(
            "Detector import error:",
            e
        )

        detect = None


    # --------------------------------------------------------
    # Start camera
    # --------------------------------------------------------

    if not camera.running:

        if not camera.start():

            print(
                "Initial camera start failed."
            )


    # --------------------------------------------------------
    # Stream loop
    # --------------------------------------------------------

    while True:

        try:

            frame = camera.get_frame()


            # ------------------------------------------------
            # No frame
            # ------------------------------------------------

            if frame is None:

                blank = create_camera_error_frame(
                    "WAITING FOR CAMERA..."
                )

                encoded = encode_frame(
                    blank,
                    quality=75
                )

                if encoded is not None:

                    yield (

                        b"--frame\r\n"

                        b"Content-Type: image/jpeg\r\n"

                        b"Cache-Control: no-cache\r\n\r\n"

                        + encoded

                        + b"\r\n"

                    )

                time.sleep(0.05)

                continue


            # ------------------------------------------------
            # Detector
            # ------------------------------------------------

            processed_frame = frame


            if detect is not None:

                try:

                    result = detect(frame)


                    if (
                        isinstance(result, tuple)
                        and
                        len(result) >= 1
                    ):

                        processed_frame = result[0]

                    elif result is not None:

                        processed_frame = result


                except Exception as e:

                    print(
                        "Detection error:",
                        e
                    )

                    processed_frame = frame


            # ------------------------------------------------
            # Encode
            # ------------------------------------------------

            encoded = encode_frame(
                processed_frame,
                quality=80
            )


            if encoded is None:

                time.sleep(0.01)

                continue


            # ------------------------------------------------
            # MJPEG
            # ------------------------------------------------

            yield (

                b"--frame\r\n"

                b"Content-Type: image/jpeg\r\n"

                b"Cache-Control: no-cache\r\n"

                b"Pragma: no-cache\r\n\r\n"

                + encoded

                + b"\r\n"

            )


            time.sleep(0.01)


        except GeneratorExit:

            print(
                "Video client disconnected."
            )

            break


        except Exception as e:

            print(
                "Video stream error:",
                e
            )

            time.sleep(0.10)


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown_camera():

    try:

        camera.release()

    except Exception as e:

        print(
            "Camera shutdown error:",
            e
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("CAMERA TEST")
    print("=" * 60)

    print(
        "Source:",
        camera.source
    )

    print(
        "Width:",
        getattr(
            config,
            "CAMERA_WIDTH",
            640
        )
    )

    print(
        "Height:",
        getattr(
            config,
            "CAMERA_HEIGHT",
            480
        )
    )

    print()


    if camera.start():

        print(
            "Camera started."
        )

        print(
            "Press Q to exit."
        )


        try:

            while True:

                frame = camera.get_frame()


                if frame is not None:

                    cv2.imshow(
                        "AI Exam Camera Test",
                        frame
                    )


                key = (
                    cv2.waitKey(1)
                    & 0xFF
                )


                if key == ord("q"):
                    break


        except KeyboardInterrupt:

            pass


        finally:

            camera.release()

            cv2.destroyAllWindows()


    else:

        print(
            "Camera test FAILED."
        )


    print()

    print(
        "Camera status:"
    )

    print(
        camera.get_status()
    )

    print()

    print("=" * 60)