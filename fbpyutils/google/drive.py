'''
https://developers.google.com/drive/api/v3/about-files
'''
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import io
import pickle
import os
import os.path

from collections import namedtuple

from typing import Tuple, Dict, List

CREDENTIALS = os.environ.get('GOOGLE_CREDENTIALS')

if not CREDENTIALS or not os.path.exists(CREDENTIALS):
    raise Exception('Credentials not provided/found. Unable to proceed.')

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

CONVERSION_INFO_FIELDS = (
    'description',
    'format',
    'mime_type',
    'conversion_code',
    'conversion_format',
    'conversion_mime_type',
    'conversion_file_extension'
)

CONVERSION_TABLE_FIELDS = (
    'conversion_code',
    'conversion_mime_type',
    'conversion_file_extension'
)

CONVERSION_INFO = (
    ('Google Docs', 'Documents', 'application/vnd.google-apps.document', 'HTML', 'HTML', 'text/html', 'html'),
    ('Google Docs', 'Documents', 'application/vnd.google-apps.document', 'HTML+ZIP', 'HTML (zipped)', 'application/zip', 'zip'),
    ('Google Docs', 'Documents', 'application/vnd.google-apps.document', 'TEXT', 'Plain text', 'text/plain', 'txt'),
    ('Google Docs', 'Documents', 'application/vnd.google-apps.document', 'RTF', 'Rich text', 'application/rtf', 'rtf'),
    ('Google Docs', 'Documents', 'application/vnd.google-apps.document', 'ODF', 'Open Office doc}', 'application/vnd.oasis.opendocument.text', 'odf'),
    ('Google Docs', 'Documents', 'application/vnd.google-apps.document', 'PDF', 'PDF', 'application/pdf', 'pdf'),
    ('Google Docs', 'Documents', 'application/vnd.google-apps.document', 'DOCX', 'MS Word document', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'docx'),
    ('Google Docs', 'Documents', 'application/vnd.google-apps.document', 'EPUB', 'EPUB', 'application/epub+zip', 'epub'),
    ('Google Sheets', 'Spreadsheets', 'application/vnd.google-apps.spreadsheet', 'XLSX', 'MS Excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx'),
    ('Google Sheets', 'Spreadsheets', 'application/vnd.google-apps.spreadsheet', 'ODS', 'Open Office sheet', 'application/x-vnd.oasis.opendocument.spreadsheet', 'ods'),
    ('Google Sheets', 'Spreadsheets', 'application/vnd.google-apps.spreadsheet', 'PDF', 'PDF', 'application/pdf', 'pdf'),
    ('Google Sheets', 'Spreadsheets', 'application/vnd.google-apps.spreadsheet', 'CSV', 'CSV (first sheet only)', 'text/csv', 'csv'),
    ('Google Sheets', 'Spreadsheets', 'application/vnd.google-apps.spreadsheet', 'TSV', '(sheet only)', 'text/tab-separated-values', 'tsv'),
    ('Google Sheets', 'Spreadsheets', 'application/vnd.google-apps.spreadsheet', 'HTML+ZIP', 'HTML (zipped)', 'application/zip', 'zip'),
    ('Google Drawing', 'Drawings', 'application/vnd.google-apps.drawing', 'JPEG', 'JPEG', 'image/jpeg', 'jpeg'),
    ('Google Drawing', 'Drawings', 'application/vnd.google-apps.drawing', 'PNG', 'PNG', 'image/png', 'png'),
    ('Google Drawing', 'Drawings', 'application/vnd.google-apps.drawing', 'SVG', 'SVG', 'image/svg+xml', 'svg'),
    ('Google Drawing', 'Drawings', 'application/vnd.google-apps.drawing', 'PDF', 'PDF', 'application/pdf', 'pdf'),
    ('Google Slides', 'Presentations', 'application/vnd.google-apps.presentation', 'PPTX', 'MS PowerPoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'pptx'),
    ('Google Slides', 'Presentations', 'application/vnd.google-apps.presentation', 'ODP', 'Open Office presentation', 'application/vnd.oasis.opendocument.presentation', 'odp'),
    ('Google Slides', 'Presentations', 'application/vnd.google-apps.presentation', 'PDF', 'PDF', 'application/pdf', 'pdf'),
    ('Google Slides', 'Presentations', 'application/vnd.google-apps.presentation', 'TEXT', 'Plain text', 'text/plain', 'txt'),
    ('Google Apps Scripts', 'Apps Scripts', 'application/vnd.google-apps.script', 'JSON', 'JSON', 'application/vnd.google-apps.script+json', 'json'),
)

GoogleDocsConversionInfo = namedtuple("GoogleDocsConversionInfo", CONVERSION_INFO_FIELDS, module='fbpyutils_google')

ObjectConversionTable = namedtuple("ObjectConversionTable", CONVERSION_TABLE_FIELDS, module='fbpyutils_google')

CONVERSION_TABLE = tuple(GoogleDocsConversionInfo._make(i) for i in CONVERSION_INFO)

GOOGLE_DRIVE_FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'

GOOGLE_MIME_TYPES = tuple(
    set([c.mime_type for c in CONVERSION_TABLE]))

DEFAULT_FILE_FIELD_LIST = 'nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size, fileExtension, parents, owners, trashed)'

DEFAULT_FOLDER_FIELD_LIST = 'nextPageToken, files(id, name, createdTime, parents, owners, trashed)'

AUTH_TOKEN = os.environ.get('GOOGLE_AUTH_TOKEN') or os.path.sep.join(
    [str(os.path.expanduser('~')),  '.google_drive_auth_token.pickle'])

def _get_conversion_table(object: Dict) -> Tuple[ObjectConversionTable, ...]:
    '''
        Returns tuple of ObjectConversionTable objects containing conversion information to Google Drive Objects.

        object
            Dictionary representing a Google Drive object

        Returns a tuple of ObjectConversionTable named tuple objects.
    '''
    return tuple(
        ObjectConversionTable._make([
            c.conversion_code,
            c.conversion_mime_type,
            c.conversion_file_extension
        ])
        for c in CONVERSION_TABLE
        if c.mime_type  == object['mimeType']
    )

def _get_conversion(object: Dict, conversion_code: str = None, conversion_table: Tuple[ObjectConversionTable, ...] = None) -> ObjectConversionTable:
    '''
        Returns an instance of ObjectConversionTable object containing conversion information for an 
        specific Google Drive Object.

        object
            Dictionary representing a Google Drive object

        conversion_code
            Code for the desired conversion. Defaults to JSON or PDF according to the object mimeType

        conversion_table
            Tuple of ObjectConversionTable objects for the Google Drive Object if it was already obtained before. 
            Defaults to None and will be fetched from the Google Drive object provided.

        Returns an ObjectConversionTable named tuple object.
    '''
    if conversion_table is None:
        conversion_table = _get_conversion_table(object)

    default = 'JSON' if object['mimeType'] in [
        'application/vnd.google-apps.script'
        ] else 'PDF'

    conversion = tuple(
            c for c in conversion_table
            if c.conversion_code == (
                default if conversion_code is None else conversion_code
                )
    )

    return None if not conversion else conversion[0]

def _get_drive_service(auth_token: str) -> Resource:
    '''
        Creates and returns an instance of Google Drive API Service.

        auth_token
            The path for the authentication token provided for a previous service authorization.
            An previous authorization is needed using authorize_service method

            This path should be stored on the OS environment variable GOOGLE_AUTH_TOKEN

        Return the instance of API service to call Google Drive methods.
    '''
    creds = None

    # The file google-drive-token.pickle stores the user's access and refresh
    # tokens, and is created automatically when the authorization flow
    # completes for the first time.
    if os.path.exists(auth_token):
        with open(auth_token, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # flow = InstalledAppFlow.from_client_secrets_file(
            #     'google-drive-credentials.json', SCOPES)
            # creds = flow.run_local_server(port=0)
            raise Exception(
                'Unable to authorize service. Run authorize_service to '
                'perform authentication.')

        # Save the credentials for the next run
        with open(auth_token, 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)


def _build_query_expression(
    file_extensions: List[str] = None,
    mime_types: List[str] = None,
    prefixes: List[str] = None,
    exclude_file_extensions: bool = False,
    exclude_mime_types: bool = False,
    exclude_prefixes: bool = False,
    trashed: bool = False
) -> str:
    ''' 
        Builds a query string to filter/search Google Drive objects. The criterias used are cummulative 
        representing information to be returned in the object list and may be reversed using the exclude
        flags options.

        file_extensions
            List of file extensions to be searched/filtered

        mime_types
            List of mime types to searched/filtered

        prefixes
            List of object names prefixes

        exclude_file_extensions
            Flag to reverse/exclude the file extensions on object list result

        exclude_mime_types
            Flag to reverse/exclude the mime types on object list result

        exclude_prefixes
            Flag to reverse/exclude the object name prefixes on object list result

        trashed
            Flag to include objects in the Google Drive Trash can

        Returns a query string with the criterias to filter/search objects in Google Drive
    '''
    file_extensions = file_extensions or []
    mime_types = mime_types or []
    prefixes = prefixes or []
    def expand(w, x, y, z):
        return ("not " if y else "") + w + (" contains " if z else "=") + "'" \
            + x + "'"

    def expand_expression(
        element, element_list, reverse=False, contains=False
    ):
        fe = ""
        connector = " and " if reverse else " or "
        if len(element_list) > 0:
            if len(element_list) > 1:
                fe = expand(element, element_list[0], reverse, contains) + \
                    connector + connector.join(
                    [expand(element, e, reverse, contains)
                        for e in element_list[1:]])
            else:
                fe = expand(element, element_list[0], reverse, contains)

        return fe

    join_list = []
    exp = expand_expression(
        'fileExtension', file_extensions, exclude_file_extensions)
    if exp:
        join_list.append(exp)

    exp = expand_expression('mimeType', mime_types, exclude_mime_types)
    if exp:
        join_list.append(exp)

    exp = expand_expression('name', prefixes, exclude_prefixes, contains=True)
    if exp:
        join_list.append(exp)

    join_list.append(
        ("not " if not trashed else "") + "trashed"
    )

    return " and ".join(join_list)


def _is_googledoc_object(object: Dict) -> bool:
    '''
        Return True if the object represents a Google Docs object (ex: Word, Spreadsheet, Presentation)

        object
            Dictionary representing a Google Drive object

        Returns True if the object is an valid Google Docs object or False if not.
    '''
    return object['mimeType'] in GOOGLE_MIME_TYPES


def _get_drive_objects(
    auth_token: str,
    file_extensions: List[str] = None,
    mime_types: List[str] = None,
    prefixes: List[str] = None,
    keywords: List[str] = None,
    exclude_file_extensions: bool = False,
    exclude_mime_types: bool = False,
    exclude_prefixes: bool = False,
    trashed: bool = False,
    page_size: int = 250,
    fields_list: str = "files(id, name, mimeType)"
) -> Tuple[Dict, ...]:
    '''
        Returns a tuple of dictionaries representing Google Drive objects based on searching/filtering 
        criterias.

        auth_token
            The path for the authentication token provided for a previous service authorization.
            An previous authorization is needed using authorize_service method.

        file_extensions
            List of file extensions to be searched/filtered

        mime_types
            List of mime types to searched/filtered

        prefixes
            List of object names prefixes

        keywords
            List of keywords to be matched on the object name

        exclude_file_extensions
            Flag to reverse/exclude the file extensions on object list result

        exclude_mime_types
            Flag to reverse/exclude the mime types on object list result

        exclude_prefixes
            Flag to reverse/exclude the object name prefixes on object list result

        trashed
            Flag to include objects in the Google Drive Trash can

        page_size
            Number of objects in each search page result

        field_list
            List of information field for each object in result list
    '''
    file_extensions = file_extensions or []
    mime_types = mime_types or []
    prefixes = prefixes or []
    keywords = keywords or []

    service = _get_drive_service(auth_token)

    q = _build_query_expression(
        file_extensions=file_extensions,
        mime_types=mime_types,
        prefixes=prefixes,
        exclude_file_extensions=exclude_file_extensions,
        exclude_mime_types=exclude_mime_types,
        exclude_prefixes=exclude_prefixes,
        trashed=trashed
    )

    # print(q)

    if "nextPageToken" not in fields_list:
        fields_list = "nextPageToken, " + fields_list

    objects = []
    page_token = None

    while True:
        response = service.files().list(
            pageSize=page_size,
            fields=fields_list,
            q=q,
            pageToken=page_token,
            spaces='drive'
        ).execute()

        for object in response.get('files', []):
            if not object.get('trashed', False):
                if object.get(
                    'mimeType', GOOGLE_DRIVE_FOLDER_MIME_TYPE
                ) != GOOGLE_DRIVE_FOLDER_MIME_TYPE:
                    object['is_google_document'] = _is_googledoc_object(object)

                    object['available_exports'] = \
                            [
                                c.conversion_code
                                for c in _get_conversion_table(object)
                            ] if object.get('is_google_document') else []

                objects.append(object)

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    include_keywords = [
        (k[1:] if k[0] == '+' else k[0:])
        for k in keywords if k[0] == '+' or k[0] != '-']

    exclude_keywords = [k[1:] for k in keywords if k[0] == '-']

    # print((include_keywords, exclude_keywords))

    # print(len(objects))

    if include_keywords:
        objects = [o for o in objects if any(
            [x for x in include_keywords if x in o['name']])]

    if exclude_keywords:
        objects = [o for o in objects if not any(
            [x for x in exclude_keywords if x in o['name']])]

    return tuple(objects)


def authorize_service() -> str:
    '''
        Provides service authorization and stores auth_token used to invoke the Google Drive services.
        This authorization and service usage requires two environment variables:
            GOOGLE_CREDENTIALS: path to project json credentials. Mandatory
            GOOGLE_AUTH_TOKEN: authorization token stored locally to authorize service calls. 
                Defaults to .google_drive_auth_token.pickle stored on user home folder

        Returns the path for the auth token created/refreshed.
    '''
    credentials = CREDENTIALS

    auth_token = AUTH_TOKEN

    scopes = SCOPES

    creds = None
    try:
        # The file google-drive-token.pickle stores the user's access and
        # refresh tokens, and is created automatically when the authorization
        # flow completes for the first time.
        if os.path.exists(auth_token):
            with open(auth_token, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials):
                    raise Exception('Credentials file not found.')
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials, scopes)
                    creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(auth_token, 'wb') as token:
                pickle.dump(creds, token)

        return auth_token
    except Exception as e:
        raise Exception("Unable to authorize service: {}".format(e))


def get_folders(
    prefixes: List[str] = None,
    keywords: List[str] = None,
    exclude_prefixes: bool = False,
    trashed: bool = False
) -> Tuple[Dict, ...]:
    '''
        Return a tuple of dictionaries with Google Drive folders objects.

        prefixes
            List of object names prefixes

        keywords
            List of keywords to be matched on the object name

        exclude_prefixes
            Flag to reverse/exclude the object name prefixes on object list result

        trashed
            Flag to include objects in the Google Drive Trash can

        Returns a tuple of Google Drive folders objects as dictionaries.
    '''
    prefixes = prefixes or []
    keywords = keywords or []

    return _get_drive_objects(
        auth_token=AUTH_TOKEN,
        file_extensions=[],
        mime_types=[GOOGLE_DRIVE_FOLDER_MIME_TYPE],
        prefixes=prefixes,
        keywords=keywords,
        exclude_prefixes=exclude_prefixes,
        trashed=trashed,
        fields_list=DEFAULT_FOLDER_FIELD_LIST
    )


def get_files(
    file_extensions: List[str] = None,
    mime_types: List[str] = None,
    prefixes: List[str] = None,
    keywords: List[str] = None,
    exclude_file_extensions: bool = False,
    exclude_mime_types: bool = False,
    exclude_prefixes: bool = False,
    trashed: bool = False
) -> Tuple[Dict, ...]:
    '''
        Return a tuple of dictionaries with Google Drive objects (No folders).

        file_extensions
            List of file extensions to be searched/filtered

        mime_types
            List of mime types to searched/filtered

        prefixes
            List of object names prefixes

        keywords
            List of keywords to be matched on the object name

        exclude_file_extensions
            Flag to reverse/exclude the file extensions on object list result

        exclude_mime_types
            Flag to reverse/exclude the mime types on object list result

        exclude_prefixes
            Flag to reverse/exclude the object name prefixes on object list result

        trashed
            Flag to include objects in the Google Drive Trash can

        Returns a tuple of Google Drive objects (No folders) as dictionaries.
    '''
    file_extensions = file_extensions or []
    mime_types = mime_types or []
    prefixes = prefixes or []
    keywords = keywords or []

    mime_types = [m for m in mime_types if m != GOOGLE_DRIVE_FOLDER_MIME_TYPE]

    objects = _get_drive_objects(
        auth_token=AUTH_TOKEN,
        file_extensions=file_extensions,
        mime_types=mime_types,
        prefixes=prefixes,
        keywords=keywords,
        exclude_file_extensions=exclude_file_extensions,
        exclude_mime_types=exclude_mime_types,
        exclude_prefixes=exclude_prefixes,
        trashed=trashed,
        fields_list=DEFAULT_FILE_FIELD_LIST
    )

    return objects


def get_parent_folders(
    object: Dict,
    folders: Tuple[Dict, ...] = None
) -> Tuple[Dict, ...]:
    '''
        Return a tuple of dictionaries with the parent folders of the Google object provided.

        object
            Dictionary representing a Google Drive object

        folders
            A tuple of folder objects (dict) previously obtained from Google Drive. This objects shoud be
            contains all folders on Google Drive or the resulting parent list may be wrong.
            Defaults to None and a new parent folders tuple objects will be fetched.

        Returns the parent folders objects for the Google object provided.
    '''
    if folders is None:
        folders = get_folders()

    def _coalesce(x):
        return None if len(x) == 0 else x[0]

    parents = []
    index = 0

    while object:
        object = _coalesce(
            [f for f in folders if f['id'] in object.get('parents', '')])
        if object:
            parents.append([index, object])
            index = index + 1

    return tuple(parents)


def get_google_drive_path(object: Dict, parents: Tuple[Dict, ...] = None, sep: str = '/', prefix: str = 'gdrive:/') -> str:
    '''
        Builds a full path for a Google Drive object from its parent folders objects.

        object
            Dictionary representing a Google Drive object

        parents
            A tuple of folder objects (dict) with the parent folders fot the object. This objects shoud be
            Defaults to None and a new parent folders tuple objects will be fetched.
        
        sep
            The path separator. Defaults to /

        prefix
            URL prefix for the path. Defaults to gdrive:/

        Returns the full path for a Google drive object.
    '''
    parents = parents or []

    if not object and not parents:
        return sep
    
    if not parents:
        parents = get_parent_folders(object)

    parent_list = list(reversed([p[1]['name'] for p in parents]))

    parent_list.append(object['name'])

    return prefix + sep + sep.join(parent_list)


def get_conversion_codes(object: Dict, mime_or_extension: str = None) -> Tuple[str, ...]:
    '''
        Returns a tuple with conversion codes to export Google Drive object in a specific file format or
        all formats available.

        object
            Dictionary representing a Google Drive object

        mime_or_extension
            Mime type or extension for the desired file format. Defaults to None and returns all formats availables.

        Returns a tuple with all conversion codes for an specific Google Drive object
    '''
    return tuple(
        c.conversion_code
        for c in _get_conversion_table(object)
        if c.conversion_mime_type == (mime_or_extension or c.conversion_mime_type)
        or c.conversion_file_extension == (mime_or_extension or c.conversion_file_extension)
    )


def get_object_bytes(object: Dict, export_as: str = None) -> bytes:
    '''
        Returns a Google Drive object content as an array of Bytes. No folder object support.

        object
            Dictionary representing a Google Drive object

        export_as
            Code for object conversion. To list available conversions, use get_conversion_codes method. 
            Defauts to default format for the object's mime type. Ignored if object is not Google Docs objects.

        Returns an array of bytes corresponding to the Google Drive object contents.
    '''
    if object.get(
        'mimeType', GOOGLE_DRIVE_FOLDER_MIME_TYPE
    ) == GOOGLE_DRIVE_FOLDER_MIME_TYPE:
        raise Exception('Impossible to download folder contents for now.')

    service = _get_drive_service(AUTH_TOKEN)

    file_id = object['id']

    if _is_googledoc_object(object):
        conversion = _get_conversion(object, conversion_code=export_as)

        if not conversion:
            raise Exception('Unable to locate conversion information to export'
                            ' as {}.'.format(
                                'DEFAULT' if export_as is None else export_as))

        request = service.files().export_media(
            fileId=file_id, mimeType=conversion.conversion_mime_type)
    else:
        request = service.files().get_media(fileId=file_id)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()

    return fh.getvalue()


def write_object_to(
    object: Dict,
    path: str,
    name: str = None,
    export_as: str = None
) -> None:
    '''
        Writes Google Drive object contents to file.

        object
            Dictionary representing a Google Drive object

        path
            Path to location where store the file. Raises an exception if the path 
            does not exists or not ends on a folder.

        nane
            Name to be used on the local file. Defaults to original Google Drive object

        export_as
            Code for object conversion. To list available conversions, use get_conversion_codes method. 
            Defauts to default format for the object's mime type. Ignored if object is not Google Docs objects.

        Writes the Google Drive object file contents and returns the full path of the stored local file.
    '''
    if not os.path.exists(path) or not os.path.isdir(path):
        raise Exception('Path doesn\'t exists or is not a folder.')

    if _is_googledoc_object(object):
        conversion = _get_conversion(object, conversion_code=export_as)
        name = name or object['name']
        fileExtension = conversion.conversion_file_extension \
            if conversion else 'FILE'
    else:
        name = ''.join(object['name'].split('.')[0:-1]) if '.' in object['name'] else object['name']
        fileExtension = object['name'].split('.')[-1] if '.' in object['name'] else object.get('fileExtension','FILE')

    file_path = os.path.sep.join([path, '.'.join([name, fileExtension])])

    data = get_object_bytes(object=object, export_as=export_as)

    with open(file_path, 'wb') as f:
        f.write(data)
        f.close()

    return file_path
