   

import logging
from typing import Any, Optional, Union, List
from ruamel.yaml.comments import CommentedMap, CommentedSeq, Comment

logger = logging.getLogger(__name__)


def update_value_preserving_comments(
    commented_obj: Union[CommentedMap, dict],
    key: Union[str, int],
    new_value: Any
) -> bool:
           
    if not isinstance(commented_obj, (CommentedMap, CommentedSeq)):
                                                                    
        commented_obj[key] = new_value
        return False

                                           
    ca = commented_obj.ca                     

                                                            
                                                              
    saved_comment = None
    if hasattr(ca, 'items') and ca.items and key in ca.items:
        saved_comment = ca.items[key]
        logger.debug(f"Preserved comment for key '{key}': {saved_comment}")

                                                         
    commented_obj[key] = new_value

                                   
    if saved_comment is not None:
                                                  
        if not hasattr(ca, 'items') or ca.items is None:
                                             
            from ruamel.yaml.comments import Comment as CommentClass
            ca.items = {}

        ca.items[key] = saved_comment
        return True

    return False


def insert_preserving_comments(
    commented_seq: Union[CommentedSeq, list],
    index: int,
    new_item: Any,
    preserve_spacing: bool = True
) -> bool:
           
    if not isinstance(commented_seq, CommentedSeq):
                                                                   
        commented_seq.insert(index, new_item)
        return False

    ca = commented_seq.ca

                                                           
                                                                         
    comments_to_shift = {}
    if hasattr(ca, 'items') and ca.items:
        for i, comment in ca.items.items():
            if isinstance(i, int) and i >= index:
                comments_to_shift[i] = comment
                logger.debug(f"Will shift comment at index {i} to {i+1}")

                                 
    commented_seq.insert(index, new_item)

                                           
    if comments_to_shift:
                            
        for old_index in comments_to_shift.keys():
            if old_index in ca.items:
                del ca.items[old_index]

                                            
        for old_index, comment in comments_to_shift.items():
            new_index = old_index + 1
            ca.items[new_index] = comment

        return True

    return False


def delete_preserving_comments(
    commented_obj: Union[CommentedMap, CommentedSeq, dict, list],
    key: Union[str, int],
    preserve_orphaned_comments: bool = True
) -> Optional[Any]:
           
                                                                 
    if isinstance(commented_obj, (CommentedSeq, list)):
        if not isinstance(key, int) or key < 0 or key >= len(commented_obj):
            logger.warning(f"Index '{key}' out of range, cannot delete")
            return None
    else:
        if key not in commented_obj:
            logger.warning(f"Key '{key}' not found in object, cannot delete")
            return None

                                   
    deleted_value = commented_obj[key]

    if not isinstance(commented_obj, (CommentedMap, CommentedSeq)):
                                                                  
        del commented_obj[key]
        return deleted_value

    ca = commented_obj.ca

                                                
    orphaned_comment = None
    if hasattr(ca, 'items') and ca.items and key in ca.items:
        orphaned_comment = ca.items[key]
        logger.debug(f"Found orphaned comment on deleted key '{key}': {orphaned_comment}")

                             
    del commented_obj[key]

                                      
    if orphaned_comment and preserve_orphaned_comments:
        if isinstance(commented_obj, CommentedMap):
                                                  
            keys = list(commented_obj.keys())
            if keys:
                next_key = keys[0]
                logger.debug(f"Attaching orphaned comment to next key '{next_key}'")
                                                    
                if hasattr(ca, 'items') and ca.items and next_key in ca.items:
                                                                      
                    ca.items[next_key] = orphaned_comment
                else:
                    if not hasattr(ca, 'items') or ca.items is None:
                        ca.items = {}
                    ca.items[next_key] = orphaned_comment

        elif isinstance(commented_obj, CommentedSeq):
                                                      
                                                                 
            if isinstance(key, int) and hasattr(ca, 'items') and ca.items:
                comments_to_shift = {}
                for i, comment in ca.items.items():
                    if isinstance(i, int) and i > key:
                        comments_to_shift[i] = comment

                                    
                for old_index in comments_to_shift.keys():
                    if old_index in ca.items:
                        del ca.items[old_index]

                                                    
                for old_index, comment in comments_to_shift.items():
                    new_index = old_index - 1
                    ca.items[new_index] = comment

                                                                          
                if len(commented_obj) > key:
                    ca.items[key] = orphaned_comment

    return deleted_value


def get_comment(
    commented_obj: Union[CommentedMap, CommentedSeq],
    key: Union[str, int]
) -> Optional[Any]:
           
    if not isinstance(commented_obj, (CommentedMap, CommentedSeq)):
        return None

    ca = commented_obj.ca
    if hasattr(ca, 'items') and ca.items and key in ca.items:
        return ca.items[key]

    return None


def set_comment(
    commented_obj: Union[CommentedMap, CommentedSeq],
    key: Union[str, int],
    comment_text: str,
    position: str = 'eol'                                                  
) -> bool:
           
    if not isinstance(commented_obj, (CommentedMap, CommentedSeq)):
        return False

    try:
                                                                
        if isinstance(commented_obj, CommentedMap):
            if position == 'eol':
                                                       
                commented_obj.yaml_add_eol_comment(comment_text, key=key)
            else:
                                              
                commented_obj.yaml_set_comment_before_after_key(key, before=comment_text)
        elif isinstance(commented_obj, CommentedSeq):
                                      
            if position == 'eol':
                commented_obj.yaml_add_eol_comment(comment_text, key)
            else:
                commented_obj.yaml_set_comment_before_after_key(key, before=comment_text)

        logger.debug(f"Set {position} comment on key '{key}': {comment_text}")
        return True
    except Exception as e:
        logger.warning(f"Failed to set comment on key '{key}': {e}")
        return False


def has_comment(
    commented_obj: Union[CommentedMap, CommentedSeq],
    key: Union[str, int]
) -> bool:
           
    return get_comment(commented_obj, key) is not None


def copy_comments(
    source_obj: Union[CommentedMap, CommentedSeq],
    target_obj: Union[CommentedMap, CommentedSeq],
    keys: Optional[List[Union[str, int]]] = None
) -> int:
           
    if not isinstance(source_obj, (CommentedMap, CommentedSeq)):
        return 0
    if not isinstance(target_obj, (CommentedMap, CommentedSeq)):
        return 0

    source_ca = source_obj.ca
    target_ca = target_obj.ca

                                  
    if not hasattr(target_ca, 'items') or target_ca.items is None:
        target_ca.items = {}

    if not hasattr(source_ca, 'items') or not source_ca.items:
        return 0

                                  
    if keys is None:
        keys = list(source_ca.items.keys())

    copied_count = 0
    for key in keys:
        if key in source_ca.items and key in target_obj:
            target_ca.items[key] = source_ca.items[key]
            copied_count += 1
            logger.debug(f"Copied comment for key '{key}'")

    return copied_count


                                      
preserve_update = update_value_preserving_comments
preserve_insert = insert_preserving_comments
preserve_delete = delete_preserving_comments
