/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   heap.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:21 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/06 12:23:22 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

int	heap_push(t_heap *h, t_request req)
{
	if (h->size >= QUEUE_MAX)
		return (0);
	h->items[h->size] = req;
	sift_up(h, h->size);
	h->size++;
	return (1);
}

t_request	*heap_peek(t_heap *h)
{
	if (h->size == 0)
		return (NULL);
	return (&h->items[0]);
}

void	heap_pop(t_heap *h)
{
	if (h->size == 0)
		return ;
	h->size--;
	h->items[0] = h->items[h->size];
	sift_down(h, 0);
}
