# Library imports
from django.http.request import HttpRequest
from django.shortcuts import render
from django.views.generic.base import TemplateView
from pm4pymdl.algo.mvp.gen_framework3 import discovery
import os
import pandas as pd
from pathlib import Path
import pickle

# Local imports
from drawpage import main, readocel
from .models import Log

BASE_DIR = Path(__file__).resolve().parent.parent

class DrawpageView(TemplateView):
    """ View for the Drawpage """

    template_name = 'drawpage.html'

    def get(self, request, *args, **kwars):
        return refresh(request, 
            file_list = [],
            object_type_list = [],
            attribute_dict = {},
            minactivity = '0',
            minedge = '0',
            clustering_method = ['', ''],
            event_assignment = ['', ''],
            dfg_file_path_list = [],
        )

    def post(self, request, *args, **kwargs):
        # Initialize returns
        file_list = []
        object_type_list = []
        attribute_dict = {}
        minactivity = '0'
        minedge = '0'
        clustering_method = ['', '']
        event_assignment = ['', '']
        dfg_file_path_list = []

        # If file_select_form
        if 'file_select' in request.POST:
            request.session['file_cookie'] = request.POST['file_select']

            # Clear old object_type_cookie and attribute_cookie
            if 'object_type_cookie' in request.session:
                del request.session['object_type_cookie']
            if 'attributes_cookie' in request.session:
                del request.session['attributes_cookie']
        elif 'object_type_select' in request.POST:
            request.session['object_type_cookie'] = request.POST['object_type_select']

            # Clear old attribute_cookie
            if 'attributes_cookie' in request.session:
                del request.session['attributes_cookie']
        elif 'attribute_select' in request.POST:
            # Save attribute_cookie
            request.session['attributes_cookie'] = request.POST.getlist('attribute_select')
        elif 'minactivity_select' in request.POST and 'minedge_select' in request.POST:
            request.session['minactivity_cookie'] = request.POST['minactivity_select']
            request.session['minedge_cookie'] = request.POST['minedge_select']

            # Call draw
            if 'file_cookie' in request.session and 'object_type_cookie' in request.session and 'attributes_cookie' in request.session and 'clustering_method_cookie' in request.session and 'event_assignment_cookie' in request.session:
                dfg_file_path_list = main.draw(request.session['object_type_cookie'], int(request.session['minactivity_cookie']), int(request.session['minedge_cookie']))

                # Remove leading '.' from file paths
                dfg_file_path_list = [sub[1 : ] for sub in dfg_file_path_list]
        elif 'clustering_method_select' in request.POST and 'event_assignment_select' in request.POST:
            request.session['clustering_method_cookie'] = request.POST['clustering_method_select']
            request.session['event_assignment_cookie'] = request.POST['event_assignment_select']

            if request.session['clustering_method_cookie'] == "kmeans":
                clustering_method = ['checked', '']
            elif request.session['clustering_method_cookie'] == "hierarchical":
                clustering_method = ['', 'checked']

            if request.session['event_assignment_cookie'] == "all":
                event_assignment = ['checked', '']
            elif request.session['event_assignment_cookie'] == "existence":
                event_assignment = ['', 'checked']

            # Call main_draw
            if 'file_cookie' in request.session and 'object_type_cookie' in request.session and 'attributes_cookie' in request.session:      
                dfg_file_path_list = self._extracted_from_post_67(request)
        return refresh(request, 
            file_list = [],
            object_type_list = object_type_list,
            attribute_dict = attribute_dict,
            minactivity = minactivity,
            minedge = minedge,
            clustering_method = clustering_method,
            event_assignment = event_assignment,
            dfg_file_path_list = dfg_file_path_list,
        )

    # TODO Rename this here and in `post`
    def _extracted_from_post_67(self, request):
        path_to_file = 'media/' + request.session['file_cookie']
        object_information = readocel.get_object_types(path_to_file)

        if 'minactivity_cookie' in request.session and 'minedge_cookie' in request.session:
            result, clustered_dataframes_list, object_and_cluster = main.main_draw(
                path_to_file,
                object_information,
                request.session['object_type_cookie'],
                request.session['clustering_method_cookie'],
                request.session['event_assignment_cookie'],
                request.session['attributes_cookie'],
                int(request.session['minactivity_cookie']),
                int(request.session['minedge_cookie']),
            )

        else:
            result, clustered_dataframes_list, object_and_cluster = main.main_draw(
                path_to_file,
                object_information,
                request.session['object_type_cookie'],
                request.session['clustering_method_cookie'],
                request.session['event_assignment_cookie'],
                request.session['attributes_cookie'],
            )
                                

        # Delete old tmp.pkl files
        Log.objects.all().delete()

        # Pickle clustered_dataframes_list
        print("################################## Pickling ...")
        for i, df in enumerate(clustered_dataframes_list):
            print("################################## Applying discovery ...")
            df.type = "succint"
            model = discovery.apply(df, parameters={"epsilon": 0, "noise_threshold": 0})
            Log.objects.create(log=pickle.dumps(df), log_model=pickle.dumps(model), log_name='tmp_' + str(i) + '.pkl')
        # Remove leading '.' from file paths
        result = [sub[1 : ] for sub in result]

        return result
        
def refresh(request: HttpRequest, file_list: list, object_type_list: list, attribute_dict: dict, minactivity: str, minedge: str, clustering_method: list, event_assignment: list, dfg_file_path_list: list):
    """Refreshes file_list, object_type_list, attribute_dict, minactivity, minedge, clustering_method, event_assignment and dfg_file_path_list

    Args:
        request (HttpRequest):
        file_list ([type]): [description]
        object_type_list ([type]): [description]
        attribute_dict ([type]): [description]
        minactivity ([type]): [description]
        minedge ([type]): [description]
        clustering_method ([type]): [description]
        event_assignment ([type]): [description]
        dfg_file_path_list ([type]): [description]

    Returns:
        HttpResponse: A rendered HttpResponse consisting of the inputted HttpRequest and the updated values for the arguments.
    """
    # Refresh file_list
    ext = ('.xmlocel','.jsonocel')
    for files in os.listdir('media/'):
        if files.endswith(ext):
            file_list.append(files)

    if 'file_cookie' in request.session:
        file_list.insert(0, request.session['file_cookie'])

        # Refresh object_type_list
        ocel_object_dict_list = readocel.get_object_types('media/' + request.session['file_cookie'])
        for i in ocel_object_dict_list:
            object_type_list.append(i.get('object_type'))
        if 'object_type_cookie' in request.session:
            object_type_list.insert(0, request.session['object_type_cookie'])

            # Refresh attribute_list
            for i in ocel_object_dict_list:
                if i.get('object_type') == request.session['object_type_cookie']:
                    for j in range(len(i.get('attributes'))):
                        if 'attributes_cookie' in request.session and i.get('attributes')[j] in request.session['attributes_cookie']:
                            attribute_dict.update({i.get('attributes')[j] : 'checked'})
                        else:
                            attribute_dict.update({i.get('attributes')[j] : ''})

    # Keep minactivity
    if 'minactivity_cookie' in request.session:
        minactivity = request.session['minactivity_cookie']

    # Keep minedge
    if 'minedge_cookie' in request.session:
        minedge = request.session['minedge_cookie']

    # Keep clustering_method
    if 'clustering_method_cookie' in request.session:
        if request.session['clustering_method_cookie'] == "kmeans":
            clustering_method = ['checked', '']
        elif request.session['clustering_method_cookie'] == "hierarchical":
            clustering_method = ['', 'checked']

    # Keep event_assignment
    if 'event_assignment_cookie' in request.session:
        if request.session['event_assignment_cookie'] == "all":
            event_assignment = ['checked', '']
        elif request.session['event_assignment_cookie'] == "existence":
            event_assignment = ['', 'checked']

    return render(request, 'drawpage.html', {
        'file_list':file_list,
        'object_type_list':object_type_list,
        'attribute_dict':attribute_dict,
        'minactivity':minactivity,
        'minedge':minedge,
        'clustering_method':clustering_method,
        'event_assignment':event_assignment,
        'dfg_file_path_list':dfg_file_path_list
    })
