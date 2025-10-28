from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MadLibTemplate
from .serializers import MadlibSerializer


@api_view(['GET'])
def get_madlib_by_id(request, madlib_id):
    """Get madlib by MongoDB ObjectId"""
    try:
        madlib = MadLibTemplate()
        result = madlib.get_by_id(madlib_id)

        if result:
            serializer = MadlibSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Madlib not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def search_madlibs(request):
    """Search madlibs by title"""
    try:
        title = request.query_params.get('title', '')

        if not title:
            return Response(
                {'error': 'Title parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        madlib = MadLibTemplate()
        results = madlib.search_by_title(title)

        serializer = MadlibSerializer(results, many=True)
        return Response({
            'madlibs': serializer.data,
            'count': len(results)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_all_madlibs(request):
    """Get all madlibs"""
    try:
        limit = int(request.query_params.get('limit', 100))

        madlib = MadLibTemplate()
        results = madlib.get_all(limit=limit)

        serializer = MadlibSerializer(results, many=True)
        return Response({
            'madlibs': serializer.data,
            'count': len(results)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
