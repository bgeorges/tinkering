from machine import Timer
import time
import gc
import binascii
 
 
class L76GNSS:
 
    GPS_I2CADDR = const(0x10)
 
    def __init__(self, pytrack=None, sda='P22', scl='P21', timeout=None):
        if pytrack is not None:
            self.i2c = pytrack.i2c
        else:
            from machine import I2C
            self.i2c = I2C(0, mode=I2C.MASTER, pins=(sda, scl))
 
        self.chrono = Timer.Chrono()
        self.timeout = timeout
        self.timeout_status = True
        self.reg = bytearray(1)
        self.i2c.writeto(GPS_I2CADDR, self.reg)
 
    def _read(self):
        self.reg = self.i2c.readfrom(GPS_I2CADDR, 128)      #Changed from 64 to 128 - I2C L76 says it can read till 255 bytes
        return self.reg
 
    def _convert_coords(self, gngll_s):
        lat = gngll_s[1]
        lat_d = (float(lat) // 100) + ((float(lat) % 100) / 60)
        lon = gngll_s[3]
        lon_d = (float(lon) // 100) + ((float(lon) % 100) / 60)
        if gngll_s[2] == 'S':
            lat_d *= -1
        if gngll_s[4] == 'W':
            lon_d *= -1
        return(lat_d, lon_d)
 
    #diff indexes from original - Using GGA sentence
    def _convert_coords1(self, gngga_s):
        lat = gngga_s[2]
        lat_d = (float(lat) // 100) + ((float(lat) % 100) / 60)
        lon = gngga_s[4]
        lon_d = (float(lon) // 100) + ((float(lon) % 100) / 60)
        if gngga_s[3] == 'S':
            lat_d *= -1
        if gngga_s[5] == 'W':
            lon_d *= -1
        return(lat_d, lon_d)
 
    def _get_time(self, gngga_s):
        gps_time = gngga_s[1]
        return(gps_time)
 
    def _get_altitude(self, gngga_s):
        gps_altitude = gngga_s[9]
        return(gps_altitude)
 
    def _get_satellites(self, gngga_s):
        num_satellites = gngga_s[7]
        return(num_satellites)
 
    def _fix_quality(self, gngga_s):
        valid = gngga_s[6]
        if valid == '0':
            return False
        else:
            return True
 
    #Using RMC sentence
    def _get_time_rmc(self, gnrmc_s):
        gps_time = gnrmc_s[1]
        return(gps_time)
 
    def _data_valid_rmc(self, gnrmc_s):
        valid = gnrmc_s[2]
        if valid == 'A':
            return True
        else:
            return False
 
    def _get_date_rmc(self, gnrmc_s):
        gps_date = gnrmc_s[9]
        return(gps_date)
 
 
    def coordinates(self, debug=False):
        lat_d, lon_d, debug_timeout = None, None, False
        if self.timeout is not None:
            self.chrono.reset()
            self.chrono.start()
        nmea = b''
        while True:
            if self.timeout is not None and self.chrono.read() >= self.timeout:
                self.chrono.stop()
                chrono_timeout = self.chrono.read()
                self.chrono.reset()
                self.timeout_status = False
                debug_timeout = True
            if not self.timeout_status:
                gc.collect()
                break
            nmea += self._read().lstrip(b'\n\n').rstrip(b'\n\n')
            gngll_idx = nmea.find(b'GNGLL')
            if gngll_idx >= 0:
                gngll = nmea[gngll_idx:]
                e_idx = gngll.find(b'\r\n')
                if e_idx >= 0:
                    try:
                        gngll = gngll[:e_idx].decode('ascii')
                        gngll_s = gngll.split(',')
                        lat_d, lon_d = self._convert_coords(gngll_s)
                    except Exception:
                        pass
                    finally:
                        nmea = nmea[(gngll_idx + e_idx):]
                        gc.collect()
                        break
            else:
                gc.collect()
                if len(nmea) > 410: # i suppose it can be safely changed to 82, which is longest NMEA frame
                    nmea = nmea[-5:] # $GNGL without last L
            time.sleep(0.1)
        self.timeout_status = True
 
        if debug and debug_timeout:
            print('GPS timed out after %f seconds' % (chrono_timeout))
            return(None, None)
        else:
            return(lat_d, lon_d)
 
    #TEST functions
    #Parser for GPGGA
    def coordinates1(self, debug=False):
        lat_d, lon_d, gps_time, valid, gps_altitude, num_satellites, debug_timeout = None, None, None, None, None, False, False
        if self.timeout is not None:
            self.chrono.reset()
            self.chrono.start()
        nmea = b''
        while True:
            if self.timeout is not None and self.chrono.read() >= self.timeout:
                self.chrono.stop()
                chrono_timeout = self.chrono.read()
                self.chrono.reset()
                self.timeout_status = False
                debug_timeout = True
            if not self.timeout_status:
                gc.collect()
                break
            nmea += self._read().lstrip(b'\n\n').rstrip(b'\n\n')
            gpgga_idx = nmea.find(b'GPGGA')
            if gpgga_idx >= 0:
                gpgga = nmea[gpgga_idx:]
                gpgga_e_idx = gpgga.find(b'\r\n')
                if gpgga_e_idx >= 0:
                    try:
                        gpgga = gpgga[:gpgga_e_idx].decode('ascii')
                        gpgga_s = gpgga.split(',')
                        lat_d, lon_d = self._convert_coords1(gpgga_s)
                        gps_time = self._get_time(gpgga_s)
                        valid = self._fix_quality(gpgga_s)
                        gps_altitude = self._get_altitude(gpgga_s)
                        num_satellites = self._get_satellites(gpgga_s)
                    except Exception:
                        pass
                    finally:
                        nmea = nmea[(gpgga_idx + gpgga_e_idx):]
                        gc.collect()
                        break
 
            else:
                gc.collect()
                if len(nmea) > 410: # i suppose it can be safely changed to 82, which is longest NMEA frame
                    nmea = nmea[-5:] # $GNGL without last L
            time.sleep(0.1)
        self.timeout_status = True
 
        if debug and debug_timeout:
            print('GPS timed out after %f seconds' % (chrono_timeout))
            return(None, None, None, None, False, None)
        else:
            return(lat_d, lon_d, gps_time, gps_altitude, valid, num_satellites)
 
    #parser for UTC time and date >> Reads GPRMC
    def get_datetime(self, debug=False):
        lat_d, lon_d, gps_time, valid, gps_date, rmc_idx, debug_timeout = None, None, None, None, None, -1, False
        if self.timeout is not None:
            self.chrono.reset()
            self.chrono.start()
        nmea = b''
        while True:
            if self.timeout is not None and self.chrono.read() >= self.timeout:
                self.chrono.stop()
                chrono_timeout = self.chrono.read()
                self.chrono.reset()
                self.timeout_status = False
                debug_timeout = True
            if not self.timeout_status:
                gc.collect()
                break
            nmea += self._read().lstrip(b'\n\n').rstrip(b'\n\n')
            #Since or spg or glonass could give date see which one is present -SEE page 10 GNSS protocol
            #GPS only       - GPRMC         GPGGA
            #Glonass only   - GNRMC         GPGGA
            #GPS+GLON       - GNRMC         GPGGA
            #No station     - GPRMC         GPGGA
            gprmc_idx = nmea.find(b'GPRMC')
            gnrmc_idx = nmea.find(b'GNRMC')
            if gprmc_idx >= 0:
                rmc_idx = gprmc_idx
            if gnrmc_idx >= 0:
                rmc_idx = gnrmc_idx
            if rmc_idx >= 0:
                rmc = nmea[rmc_idx:]
                rmc_e_idx = rmc.find(b'\r\n')
                if rmc_e_idx >= 0:
                    try:
                        rmc = rmc[:rmc_e_idx].decode('ascii')
                        rmc_s = rmc.split(',')
                        lat_d, lon_d = self._convert_coords1(rmc_s[1:])
                        gps_time = self._get_time_rmc(rmc_s)
                        valid = self._data_valid_rmc(rmc_s)
                        gps_date = self._get_date_rmc(rmc_s)
                    except Exception:
                        pass
                    finally:
                        nmea = nmea[(rmc_idx + rmc_e_idx):]
                        gc.collect()
                        break
 
            else:
                gc.collect()
                if len(nmea) > 512: # i suppose it can be safely changed to 82, which is longest NMEA frame --CHANGED to 512
                    nmea = nmea[-5:] # $GNGL without last L
            time.sleep(0.1)
        self.timeout_status = True
 
        if debug and debug_timeout:
            print('GPS timed out after %f seconds' % (chrono_timeout))
            return(None, None, None, False, None)
        else:
            return(lat_d, lon_d, gps_time, valid, gps_date)