import cv2
import copy
import math


capture = cv2.VideoCapture(0)

while(True):

    ret, image = capture.read()
    image = cv2.resize(image, (500, 400))  # задали размер
    image = cv2.flip(image, 1)  # отзеркалили изображение

    # собираем информацию с конкретного участка видеоизображения
    space = image[50:316, 250:500]  # задали границы
    cv2.rectangle(image, (250, 50), (500, 316), (255, 255, 255), 2)  # обозначили рамку на входном изображении

    # надписи на окне съемки
    text_1 = "Press y for capturing!"
    text_2 = "Press z for calculating!"
    text_3 = "Press q for quit!"
    cv2.putText(image, text_1, (7, 15), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(image, text_2, (7, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(image, text_3, (7, 45), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    # выводим изображение с камеры
    cv2.imshow('Camera!', image)

    # делаем скриншот клавишей Y
    if cv2.waitKey(1) & 0xFF == ord('y'):
        cv2.imwrite('images/screenshot.png', space)
        print("You've taken a screenshot!")

    # Закрытие камеры при нажатии клавиши Z, начало обработки
    if cv2.waitKey(1) & 0xFF == ord('z'):
        picture = cv2.imread('images/screenshot.png')  # импортируем полученную картинку
        # делаем необходимые для дальнейшей работы преобразования
        gray = cv2.cvtColor(picture, cv2.COLOR_BGR2GRAY)  # сделали картинку в серых тонах
        # cv2.imshow('Gray!', gray)
        blurred_picture = cv2.GaussianBlur(gray, (5, 5), 0)  # размытие по Гауссу, чтобы шум рамки не считался краем
        # cv2.imshow('Blurred!', blurred_picture)
        ret, thresh = cv2.threshold(blurred_picture, 127, 255, cv2.THRESH_BINARY_INV)  # бинаризация по Оцу
        cv2.imshow('Thresh!', thresh)  # выводим полученное изображение

        thresh1 = copy.deepcopy(thresh)  # копирование преобразованного скриншота
        contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # поиск контуров

        # находим контуры руки, отделяя их от фона по величене занимаемой площади
        max_area = 0

        if len(contours) > 0:

            for i in range(len(contours)):
                x = contours[i]
                area = cv2.contourArea(x)

                if area > max_area:
                    max_area = area
                    sel_i = i  # выбранные i

            sel_contours = contours[sel_i]  # выбранные контуры
            hull = cv2.convexHull(sel_contours)  # оболочка руки

            cv2.drawContours(picture, sel_contours, -1, (0, 255, 0), 2)
            cv2.drawContours(picture, hull, -1, (0, 0, 255), 3)
            # cv2.imshow('Contours!', picture)

        #  ищем дефекты выпуклости
        hull = cv2.convexHull(sel_contours, returnPoints=False)

        if len(hull) > 3:
            defects = cv2.convexityDefects(sel_contours, hull)

            if type(defects) != type(None):  # проверка на ошибки
                fingers = 0

                for i in range(defects.shape[0]):  # рассчитываем угол
                    s, e, f, d = defects[i][0]
                    start = tuple(sel_contours[s][0])
                    end = tuple(sel_contours[e][0])
                    far = tuple(sel_contours[f][0])

                    a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                    b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                    c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                    angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))  # по теореме косинусов

                    if angle <= math.pi / 2:  # острые углы считаются пальцем
                        fingers += 1
                        cv2.circle(picture, far, 8, [211, 84, 0], -1)  # отмечаем промежутки между пальцами

            # cv2.imshow('Defects!', picture)

            # вывод финальных данных
            if fingers == 0:
                message = "You're showing a fist or pointing!"
            elif fingers == 1:
                message = "You're showing a Victory sign or 2 fingers!"
            elif fingers == 2:
                message = "You're showing a Crown or 3 fingers!"
            elif fingers == 3:
                message = "You're showing an OK sign or 4 fingers!"
            elif fingers == 4:
                message = "You're showing a Hi sign or 5 fingers!"
            elif fingers == 5:
                message = "Wow! You're a monster!"
            elif fingers == 6:
                message = "Unbelievable amount of fingers!"
            else:
                message = "Stop it! Right now!"

            cv2.putText(picture, message, (7, 15), cv2.FONT_HERSHEY_COMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow('Final!', picture)  # отображаем проведенный анализ

    # выйти из программы с клавишой Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# закрытие камеры
capture.release()
cv2.destroyAllWindows()
