/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   call_algo.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/15 12:14:03 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/19 16:51:39 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	call_algo(char **argv)
{
	int	flag;
	int	i;

	flag = 0;
	i = 1;
	if (argv[i] == NULL)
		return (0);
	if (strcmp_original(argv[i], "--simple"))
		flag = 1;
	else if (strcmp_original(argv[i], "--medium"))
		flag = 2;
	else if (strcmp_original(argv[i], "--complex"))
		flag = 3;
	else if (strcmp_original(argv[i], "--adaptive"))
		flag = 4;
	return (flag);
}
