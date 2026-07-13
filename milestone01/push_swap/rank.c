/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   rank.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/14 15:54:20 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/18 13:27:40 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	make_rank(t_list **a_lst)
{
	t_list			*tmp;
	t_list			*curr;
	unsigned int	rank;

	curr = *a_lst;
	while (curr)
	{
		rank = 0;
		tmp = *a_lst;
		while (tmp)
		{
			if (tmp->content < curr->content)
				rank++;
			tmp = tmp->next;
		}
		curr->rank = rank;
		curr = curr->next;
	}
}
