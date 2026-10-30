/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   cleanup.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:24:03 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/06 12:24:04 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "codexion.h"

static void	destroy_base(t_table *t)
{
	if (t->ready_base > 0)
		pthread_mutex_destroy(&t->stop_mutex);
	if (t->ready_base > 1)
		pthread_mutex_destroy(&t->log_mutex);
	if (t->ready_base > 2)
		pthread_mutex_destroy(&t->arbiter);
	if (t->ready_base > 3)
		pthread_cond_destroy(&t->ready);
}

void	destroy_table(t_table *t)
{
	int	i;

	i = 0;
	while (i < t->ready_coders)
	{
		pthread_mutex_destroy(&t->coders[i].state_mutex);
		pthread_cond_destroy(&t->coders[i].wake);
		i++;
	}
	i = 0;
	while (i < t->ready_dongles)
	{
		pthread_mutex_destroy(&t->dongles[i].mutex);
		i++;
	}
	destroy_base(t);
	free(t->coders);
	free(t->dongles);
}
