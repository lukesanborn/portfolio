import math
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils import tables
from utils.datasets import LoadStreams, Load_Frc_Webcam
from utils.general import check_img_size, non_max_suppression, scale_coords, \
    set_logging
from utils.plots import plot_one_box, plot_one_box_noshow
from utils.torch_utils import select_device, time_synchronized


class cameraConstant:
    # Object sizes
    foreshortening = 1.1547
    marker_width = 3.5
    powercell_width = 7

    marker_width = marker_width * foreshortening
    powercell_width = powercell_width * foreshortening

    # Camera settings
    focal = 227.15
    sensor_height = 2.4
    sensor_height_pixels = 144
    # object_height_inframe = (sensor_height * box_width)/sensor_height_pixels

def tracking_object_width(tracking_name):
    return cameraConstant.powercell_width if tracking_name == 'powercell' else cameraConstant.marker_width

def calc_distance(box_width, tracking_object):
    if box_width:
        tracking_object = tracking_object_width(tracking_object)
        return (tracking_object * cameraConstant.focal) / box_width
    else:
        return 0
def calc_theta(centery, distance, box_width_pixels, center_header, tracking_object):
    align = True if centery >= center_header else False
    adjacent_pixels = abs(centery - center_header)
    adjacent_ratio = tracking_object_width(tracking_object)*adjacent_pixels/box_width_pixels
    header = math.acos(adjacent_ratio/distance)
    header = 90 - header*(180/math.pi)
    return header if align else -header

# noinspection PyPackageRequirements
def detect(weights, source, imgsz, conf_thres, iou_thres, device, view_img, agnostic_nms, augment, output):
    webcam = source.isnumeric()
    frc = source.endswith('frc')

    # Initialize
    set_logging()
    device = select_device(output, device)
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # start network table
    if frc:
        network_table = tables.table("VisionPi")
        network_table.set_logging("DEBUG")

    # Load model
    model = attempt_load(weights, map_location=device, output=output)  # load FP32 model
    imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size
    if half:
        model.half()  # to FP16

    if webcam:
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(output, source, img_size=imgsz)
    else:
        # default to showing image
        dataset = Load_Frc_Webcam(img_size=imgsz)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
    for path, img, im0s, vid_cap in dataset:
        data = []
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment=augment)[0]

        # Apply NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, agnostic=agnostic_nms)
        t2 = time_synchronized()

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if webcam:  # batch_size >= 1
                p, s, im0, frame = path[i], '%g: ' % i, im0s[i].copy(), dataset.count
            else:
                p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            s += '%gx%g ' % img.shape[2:]  # print string
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    label = names[int(cls)]
                    if view_img:  # Add bbox to image

                        lower, upper, name = plot_one_box(xyxy, im0, label=label, color=colors[int(cls)],
                                                          line_thickness=3)
                    else:
                        lower, upper = plot_one_box_noshow(xyxy, im0, label=label, color=colors[int(cls)],
                                                           line_thickness=3)
                    centerx = round((lower[1] + upper[1]) / 2, 3)
                    centery = round(((lower[0] + upper[0]) / 2), 3)
                    distance = round(calc_distance(upper[0] - lower[0], label), 3)
                    center_header = 256 / 2  # 128
                    theta = calc_theta(centery, distance, upper[1]-lower[1], center_header, label)
                    data.append([int(cls), distance, theta, centerx, centery])
                    # print([int(cls), round(calc_distance(upper[0] - lower[0], label), 3), centerx, centery])
            if True:
                print(f'{s}Done. ({t2 - t1:.3f}s)')

            # Stream results
            if view_img and not frc:
                # show window
                cv2.imshow(str(p), im0)
            if frc and view_img:
                # frc streaming
                dataset.output_stream.putFrame(im0)

            if data and frc:
                print("Data: ", data)
                data = np.array(data)
                data = data.astype('float64')
                if data.shape.__len__() == 1:
                    data = np.reshape(data, (1, data.size))
                else:
                    pass

                # id, distance, head, xcenter, ycenter, state
                network_table.add_array('id', data[:, 0])
                network_table.add_array('distances', data[:, 1])
                network_table.add_array('head', data[:, 2])
                network_table.add_array('xcenter', data[:, 3])
                network_table.add_array('ycenter', data[:, 4])
                network_table.add_float('state', 0)


if __name__ == '__main__':
    with torch.no_grad():
        detect(weights='best3000.pt', source='frc', imgsz=256, conf_thres=0.25, iou_thres=0.45, device='',
               view_img=True,
               agnostic_nms=False, augment=False, output=False)
