import os
from django.conf import settings
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import datetime
from apps.app.models import Human
from apps.utils.print_colors import _red, _green
from apps.utils.shortcuts import get_object_or_none
from . import serializers
from rest_framework.viewsets import ModelViewSet
import base64
import io
from imageio import imread, imwrite

import cv2
from . import ocr
import os
from PIL import Image
import face_recognition
from django.core.files import File
import numpy as np
import logging


logger = logging.getLogger(__name__)


class HumanViewSet(ModelViewSet):
    serializer_class = serializers.HumanSerializer
    queryset = Human.objects.all()

    def str_to_image2(self, base64_string):
        imgdata = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(imgdata))
        image = np.array(image)
        return image

    def str_to_image(self, base64_string):
        imgdata = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(imgdata))
        image = np.array(image)
        image = image[:, :, ::-1].copy()
        return image

    def get_path(self, path, file):
        return default_storage.save('{}/'.format(path) + str(file), ContentFile(file.read()))

    def create(self, request, *args, **kwargs):
        response = {
            'success': True
        }
        cam_photo = request.data['cam_photo']
        cam_photo_im = self.str_to_image(cam_photo)
        cv2.imwrite('temp0.jpg', cam_photo_im)
        cp = open(os.path.join('temp0.jpg'), 'rb')
        cp_file = File(cp)


        cover_img = request.data['cover']['value']
        cover_img = self.str_to_image2(cover_img)
        imwrite('temp.jpg', cover_img)
        f_c = open(os.path.join('temp.jpg'), 'rb')
        cover_file = File(f_c)

        ocr_o_cover = ocr.ocr_o(cover_img)
        back_cover_img = request.data['back_cover']['value']
        back_cover_img = self.str_to_image2(back_cover_img)
        imwrite('temp2.jpg', back_cover_img)
        f_bc = open(os.path.join('temp2.jpg'), 'rb')
        back_cover_file = File(f_bc)

        os.remove(os.path.join('temp.jpg'))
        os.remove(os.path.join('temp2.jpg'))

        ocr_o_back_cover = ocr.ocr_o(back_cover_img)

        ocr_o_back_cover.prepare_im()
        ocr_o_cover.prepare_im()
        info = ocr_o_cover.get_cover_info()
        cc, name, last_name, img = info

        if str(request.data['dni']) != cc:
            response['mensaje'] = "No coinciden los numeros de id."
            response['id_1'] = str(request.data['dni'])
            response['id_2'] = cc
            response['success'] = False
            response['dni_not_match'] = True
        else:
            print("Numeros de id correctos.")

        height, width, channels = cover_img.shape
        # crop_img = cover_img[int(height * 0.3):int(height * 0.86), int(width * 0.55):width]
        # cv2.imwrite("rrr.jpg", crop_img)
        # print(crop_img.shape)
        # print(face_recognition.face_encodings(crop_img))
        # crop_img_encodings = face_recognition.face_encodings(crop_img)[0]

        """
        known_face_encodings = [
            crop_img_encodings
        ]

        known_face_names = [
            name + " " + last_name
        ]

        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        frame = cam_photo_im
        print(cam_photo_im.shape)

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        rgb_small_frame = small_frame[:, :, ::-1]

        if process_this_frame:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            print(name)
            
        cv2.imwrite('testt.jpg', crop_img)
            
        """

        print("cc: {}".format(cc))
        print("nombre: {}".format(name))
        print("apellido: {}".format(last_name))

        date = ocr_o_back_cover.get_back_cover_info()
        print("Fecha de nacimiento: {}".format(date))

        if str(request.data['dni']) == cc and name != "Unknown":

            # set path file
            path = self.get_path(path=cc, file=cover_file)
            path_back = self.get_path(path=cc, file=back_cover_file)

            dni = request.data['dni']

            if get_object_or_none(Human, dni=dni) is None:

                Human.objects.create(
                    first_name=request.data['first_name'],
                    last_name=request.data['last_name'],
                    dni=dni,
                    birth_date=request.data['date'],
                    cover_dni=path,
                    back_cover_dni=path_back,
                    photo=cp_file
                )
                response['mensaje'] = 'Persona creada con exito'
            else:
                response['success'] = False
                response['mensaje'] = 'Esta persona ya existe!'
        else:
            response['mensaje'] = 'Persona desconocida'
            response['success'] = False
            response['unknown'] = True

        return Response(response)


class LoginViewSet(HumanViewSet):

    def create(self, request, *args, **kwargs):
        photo = self.str_to_image(request.data['photo'])
        response = {
            'success': True,
            'data': None
        }
        cc = request.data['cc']
        human = get_object_or_none(Human, dni=cc)

        if human:
            name = human.get_full_name()
            path = os.path.join(settings.MEDIA_ROOT, human.photo.name)
            im = cv2.imread(path)
            cv2.imwrite("foto.jpg", im)
            img_encodings = face_recognition.face_encodings(im)[0]
            known_face_encodings = [
                img_encodings
            ]

            known_face_names = [
                name
            ]

            face_locations = []
            face_encodings = []
            face_names = []
            process_this_frame = True

            frame = photo
            #print(photo.shape)

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            #cv2.imwrite("ff.jpg", small_frame)

            rgb_small_frame = small_frame[:, :, ::-1]
            if process_this_frame:
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    if True in matches:
                        first_match_index = matches.index(True)
                        name = known_face_names[first_match_index]

                    face_names.append(name)

            process_this_frame = not process_this_frame

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                # print(name)
            # print(name)
            if name != "Unknown" and len(face_names) == 1:
                print('login :D')
                response['mensaje'] = 'Login exitoso'
                response['dni'] = human.dni
                response['date'] = human.birth_date
                response['dni_back'] = human.back_cover_dni.url
                response['dni_front'] = human.cover_dni.url
                response['photo'] = human.photo.url
                response['full_name'] = human.get_full_name()
                response['success'] = True
            else:
                print('nop')
                logger.error('login: nop login')
                response['mensaje'] = 'Persona desconocida'
                response['success'] = False
        else:
            print('doesnt exist!')
            logger.error('login: doesnt exist')
            response['mensaje'] = 'Esta persona no existe'
            response['success'] = False
        return Response(response)


class CheckFaceViewSet(HumanViewSet):
    def create(self, request, *args, **kwargs):
        photo = self.str_to_image(request.data['photo'])
        response = {
            'pass': True
        }
        cc = request.data['cc']
        human = get_object_or_none(Human, dni=cc)

        if human:
            name = human.get_full_name()
            path = os.path.join(settings.MEDIA_ROOT, human.photo.name)
            im = cv2.imread(path)
            img_encodings = face_recognition.face_encodings(im)[0]
            known_face_encodings = [
                img_encodings
            ]

            known_face_names = [
                name
            ]

            face_locations = []
            face_encodings = []
            face_names = []
            process_this_frame = True

            frame = photo
            # print(photo.shape)

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # cv2.imwrite("ff.jpg", small_frame)

            rgb_small_frame = small_frame[:, :, ::-1]
            if process_this_frame:
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    if True in matches:
                        first_match_index = matches.index(True)
                        name = known_face_names[first_match_index]

                    face_names.append(name)

            process_this_frame = not process_this_frame

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                # print(name)
            # print(name)
            if name != "Unknown" and len(face_names) == 1:
                print('active')
                response['pass'] = True
            else:
                print('nop')
                logger.error('login: nop login')
                response['pass'] = False
        else:
            print('doesnt exist!')
            logger.error('login: doesnt exist')
            response['pass'] = False
            #response['mensaje'] = 'Esta persona no existe'
            #response['success'] = False
        return Response(response)

