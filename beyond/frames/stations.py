import numpy as np
from .frames import Frame, WGS84, _MetaFrame
from ..constants import Earth
from ..utils.matrix import rot2, rot3


class TopocentricFrame(Frame):
    """Base class for ground station
    """

    _rotation_before_translation = True

    @classmethod
    def visibility(cls, orb, start=None, stop=None, step=None, events=False, delay=False):
        """Visibility from a topocentric frame

        Args:
            orb (Orbit): Orbit to compute visibility from the station with
            start (Date): starting date of the visibility search
            stop (Date or datetime.timedelta) end of the visibility search
            step (datetime.timedelta): step of the computation
            events (bool, Listener or list): If evaluate to True, compute
                AOS, LOS and MAX elevation for each pass on this station.
                If 'events' is a Listener or an iterable of Listeners, they
                will be added to the computation
            delay (bool): If True, the yielded orbits will be computed in a way
                to have their ``delayed_date`` attribute match the steps, instead of
                the normal ``date`` attribute. This allow to compute fixed steps
                from a station standpoint.

        Yield:
            Orbit: In-visibility point of the orbit. This Orbit is already
            in the frame of the station and in spherical form.
        """

        from ..orbits.listeners import stations_listeners, Listener

        listeners = []
        events_classes = tuple()

        if events:
            # Handling of the listeners passed in the 'events' kwarg
            if isinstance(events, Listener):
                listeners.append(events)
            elif isinstance(events, (list, tuple)):
                listeners.extend(events)

            sta_list = stations_listeners(cls)
            listeners.extend(sta_list)

            # Retrieve the list of events associated with the desired listeners
            events_classes = tuple(listener.event for listener in sta_list)

        for point in orb.iter(start=start, stop=stop, step=step, listeners=listeners):

            point.frame = cls
            point.form = 'spherical'

            # Not very clean !
            if point.phi < 0 and not isinstance(point.event, events_classes):
                continue

            if delay and not point.event:
                # Compute the delay and retro-propagate
                date = point.date
                while point.delayed_date != date:
                    point = point.propagate(date - point.delay)
                    point.frame = cls
                    point.form = "spherical"

            yield point

    @classmethod
    def _geodetic_to_cartesian(cls, lat, lon, alt):
        """Conversion from latitude, longitue and altitude coordinates to
        cartesian with respect to an ellipsoid

        Args:
            lat (float): Latitude in radians
            lon (float): Longitue in radians
            alt (float): Altitude to sea level in meters

        Return:
            numpy.array: 3D element (in meters)
        """
        C = Earth.r / np.sqrt(1 - (Earth.e * np.sin(lat)) ** 2)
        S = Earth.r * (1 - Earth.e ** 2) / np.sqrt(1 - (Earth.e * np.sin(lat)) ** 2)
        r_d = (C + alt) * np.cos(lat)
        r_k = (S + alt) * np.sin(lat)

        norm = np.sqrt(r_d ** 2 + r_k ** 2)
        return norm * np.array([
            np.cos(lat) * np.cos(lon),
            np.cos(lat) * np.sin(lon),
            np.sin(lat)
        ])


def create_station(name, latlonalt, parent_frame=WGS84, orientation='N'):
    """Create a ground station instance

    Args:
        name (str): Name of the station

        latlonalt (tuple of float): coordinates of the station, as follow:

            * Latitude in degrees
            * Longitude in degrees
            * Altitude to sea level in meters

        parent_frame (Frame): Planetocentric rotating frame of reference of
            coordinates.
        orientation (str or float): Heading of the station
            Acceptables values are 'N', 'S', 'E', 'W' or any angle in radians

    Return:
        TopocentricFrame
    """

    if isinstance(orientation, str):
        orient = {'N': np.pi, 'S': 0., 'E': np.pi / 2., 'W': 3 * np.pi / 2.}
        orientation = orient[orientation]

    latlonalt = list(latlonalt)
    latlonalt[:2] = np.radians(latlonalt[:2])
    coordinates = TopocentricFrame._geodetic_to_cartesian(*latlonalt)

    def _convert(self):
        """Conversion from Topocentric Frame to parent frame
        """
        lat, lon, _ = self.latlonalt
        m = rot3(-lon) @ rot2(lat - np.pi / 2.) @ rot3(self.orientation)
        offset = np.zeros(6)
        offset[:3] = self.coordinates
        return self._convert(m, m), offset

    mtd = '_to_%s' % parent_frame.__name__
    dct = {
        mtd: _convert,
        'latlonalt': latlonalt,
        'coordinates': coordinates,
        'parent_frame': parent_frame,
        'orientation': orientation
    }
    cls = _MetaFrame(name, (TopocentricFrame,), dct)
    cls + parent_frame

    return cls