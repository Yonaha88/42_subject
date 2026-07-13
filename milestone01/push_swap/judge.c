/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   judge.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/14 17:24:09 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/18 13:27:18 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	judge(t_list **a_lst, t_list **b_lst)
{
	t_list	*lst;

	lst = *a_lst;
	while (lst != NULL && lst->next != NULL)
	{
		if (lst->rank > lst->next->rank || (lst->rank + 1 < lst->next->rank))
			return (-1);
		lst = lst->next;
	}
	if (*b_lst != NULL)
		return (-1);
	return (1);
}
