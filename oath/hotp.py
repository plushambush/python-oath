import hashlib
import hmac
import binascii

'''
HOTP implementation

To compute an HOTP one-time-password:

    >>> hotp(key, counter)

where is the hotp is a key given as an hexadecimal string and counter is an
integer. The counter value must be kept synchronized on the server and the
client side. 

See also http://tools.ietf.org/html/rfc4226
'''

__ALL__ = ( 'hotp', 'accept_hotp' )

def truncated_value(h):
    bytes = map(ord, h)
    offset = bytes[-1] & 0xf
    v = (bytes[offset] & 0x7f) << 24 | (bytes[offset+1] & 0xff) << 16 | \
            (bytes[offset+2] & 0xff) << 8 | (bytes[offset+3] & 0xff)
    return v

def dec(h,p):
    v = str(truncated_value(h))
    return v[len(v)-p:]

def int2beint64(i):
    hex_counter = hex(long(i))[2:-1]
    hex_counter = '0' * (16 - len(hex_counter)) + hex_counter
    bin_counter = binascii.unhexlify(hex_counter)
    return bin_counter

def __hotp(key, counter, hash=hashlib.sha1):
    bin_counter = int2beint64(counter)
    bin_key = binascii.unhexlify(key)

    return hmac.new(bin_key, bin_counter, hash).digest()

def hotp(key,counter,format='dec6',hash=hashlib.sha1):
    '''
       Compute a HOTP value as prescribed by RFC4226

       :params key: 
           the HOTP secret key given as an hexadecimal string
       :params counter:
           the OTP generation counter
       :params format:
           the output format, can be:
              - hex, for a variable length hexadecimal format,
              - hex-notrunc, for a 40 characters hexadecimal non-truncated format,
              - dec4, for a 4 characters decimal format,
              - dec6,
              - dec7, or
              - dec8
           it defaults to dec6.
       :params hash:
           the hash module (usually from the hashlib package) to use,
           it defaults to hashlib.sha1.

       :returns:
           a string representation of the OTP value (as instructed by the format parameter).

       Examples:

        >>> hotp('343434', 2, format='dec6')
            '791903'
    '''
    bin_hotp = __hotp(key, counter, hash)

    if format == 'dec4':
        return dec(bin_hotp, 4)
    elif format == 'dec6':
        return dec(bin_hotp, 6)
    elif format == 'dec7':
        return dec(bin_hotp, 7)
    elif format == 'dec8':
        return dec(bin_hotp, 8)
    elif format == 'hex':
        return hex(truncated_value(bin_hotp))[2:]
    elif format == 'hex-notrunc':
        return binascii.hexlify(bin_hotp)
    elif format == 'bin':
        return bin_hotp
    elif format == 'dec':
        return str(truncated_value(bin_hotp))
    else:
        raise ValueError('unknown format')

def accept_hotp(key, response, counter, format='dec6', hash=hashlib.sha1,
        drift=3, backward_drift=0):
    '''
       Validate a HOTP value inside a window of
       [counter-backward_drift:counter+forward_drift]

       :params key:
           the shared secret
       :type key:
           hexadecimal string of even length
       :params response:
           the OTP to check
       :type response:
           ASCII string
       :params counter:
           value of the counter running inside an HOTP token, usually it is
           just the count of HOTP value accepted so far for a given shared
           secret; see the specifications of HOTP for more details;
       :params format:
           the output format, can be:
             - hex40, for a 40 characters hexadecimal format,
             - dec4, for a 4 characters decimal format,
             - dec6,
             - dec7, or
             - dec8
           it defaults to dec6.
       :params hash:
           the hash module (usually from the hashlib package) to use,
           it defaults to hashlib.sha1.
       :params drift:
           how far we can look forward from the current value of the counter
       :params backward_drift:
           how far we can look backward from the current counter value to
           match the response, default to zero as it is usually a bad idea to
           look backward as the counter is only advanced when a valid value is
           checked (and so the counter on the token side should have been
           incremented too)

       :returns:
           a pair of a boolean and an integer:
            - first is True if the response is validated and False otherwise,
            - second is the new value for the counter; it can be more than
              counter + 1 if the drift window was used; you must store it if
              the response was validated.

       >>> accept_hotp('343434', '122323', 2, format='dec6')
           (False, 2)

       >>> hotp('343434', 2, format='dec6')
           '791903'

       >>> accept_hotp('343434', '791903', 2, format='dec6')
           (True, 3)

       >>> hotp('343434', 3, format='dec6')
           '907279'

       >>> accept_hotp('343434', '907279', 2, format='dec6')
           (True, 4)
    '''

    for i in range(-backward_drift, drift+1):
        if hotp(key, counter+i, format=format, hash=hash) == str(response):
            return True, counter+i+1
    return False,counter