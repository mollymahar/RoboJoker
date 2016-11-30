from uuid import uuid4
import boto
import os.path
from flask import current_app as app
from werkzeug.utils import secure_filename


def s3_upload(source_file, upload_dir=None, acl='public-read'):
    """ Uploads WTForm File Object to Amazon S3
        Expects following app.config attributes to be set:
            S3_KEY              :   S3 API Key
            S3_SECRET           :   S3 Secret Key
            S3_BUCKET           :   What bucket to upload to
            S3_UPLOAD_DIRECTORY :   Which S3 Directory.
        The default sets the access rights on the uploaded file to
        public-read.  It also generates a unique filename via
        the uuid4 function combined with the file extension from
        the source file.
    """

    if upload_dir is None:
        upload_dir = ""

    source_filename = secure_filename('test.json')
    source_extension = os.path.splitext(source_filename)[1]

    destination_filename = uuid4().hex + source_extension

    # Connect to S3 and upload file.
    conn = boto.connect_s3("AKIAJ3WTOWBSWNVKNLCQ", "3DX98+5PSxplKYxJ64POmZ8M5PDJMfmw3XITdlbm")
    b = conn.get_bucket("robojoker")

    sml = b.new_key("/".join([upload_dir, destination_filename]))
    sml.set_contents_from_string(source_file)
    sml.set_acl(acl)

    return destination_filename