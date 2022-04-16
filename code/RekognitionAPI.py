import boto3
from botocore.config import Config

"""
Module sets up Recokgnition API class.

The class is used to call detect faces, recognize, and compare faces features of
the API.
"""

class RekognitionAPI():
    """
    RekognitionAPI class with key functions.

    Member config: configuration object for API call.
    Member client: Rekognition client object for function calls.
    """
    def __init__(self):
        """
        Initialize object, set up members
        """
        self.config = Config(region_name = 'XXXX')
        self.client=boto3.client('rekognition',config=self.config,
             aws_access_key_id="XXXX",
             aws_secret_access_key= "XXXX")

    def detect_faces(self,photo):
        """
        Function takes an image and identifies facial features.

        For each face detected, facial features are stored as well. Gender value
        is only stored if there is 85%+ probability of API saying that it is the
        identified gender.

        Parameter photo: image to detect faces in
        """
        try:
            img=open(photo,'rb')
            response = self.client.detect_faces(Image={'Bytes': img.read()},Attributes=['ALL'])
            matches = []
            for i in response['FaceDetails']: # store facial features for each face
                genderV = i['Gender']['Value']
                genderP = i['Gender']['Confidence']
                roll = i['Pose']['Roll']
                yaw = i['Pose']['Yaw']
                pitch = i['Pose']['Pitch']
                if genderP > 85:
                    gender = genderV
                else:
                    gender = 'NA'
                #if yaw >= -75 and yaw <= 75: # hard to detect faces
                matches.append([gender,roll,yaw,pitch])
            return matches
        except ClientError:
            return -1

    def recognize(self,photo):
        """
        Function takes an image and recognize celebrities.

        Some astronauts have celebrity status in the API so they can be directly
        matched.

        Parameter photo: image to recognize faces in
        """
        with open(photo, 'rb') as image:
            response = self.client.recognize_celebrities(Image={'Bytes': image.read()})
        matches = []
        for celebrity in response['CelebrityFaces']:
            matches.append(celebrity['Name']) # could be incorrect spelling
        return(matches)

    def compare_faces(self,sourceFile, targetFile):
        """
        Function takes an image and recognize celebrities.

        When astronauts are undetected by recognize_celebrities, then they have
        to be compared with source photos of astronauts one by one.

        Parameter sourceFile: face A to compare
        Parameter targetFile: face B to compare
        """
        imageSource=open(sourceFile,'rb')
        imageTarget=open(targetFile,'rb')
        response=self.client.compare_faces(SimilarityThreshold=80,
                                      SourceImage={'Bytes': imageSource.read()},
                                      TargetImage={'Bytes': imageTarget.read()})
        for faceMatch in response['FaceMatches']: # check against each face in photo
            position = faceMatch['Face']['BoundingBox']
            similarity = str(faceMatch['Similarity'])
            # print('The face at ' +
            #        str(position['Left']) + ' ' +
            #        str(position['Top']) +
            #        ' matches with ' + similarity + '% confidence')

        imageSource.close()
        imageTarget.close()
        return len(response['FaceMatches'])
